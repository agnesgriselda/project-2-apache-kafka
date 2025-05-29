from fastapi import FastAPI, HTTPException, Query, Path as FastApiPath
from pydantic import BaseModel, Field
from typing import List, Union

# Tidak perlu import SparkSession di sini jika models_loader sudah menanganinya
# from pyspark.sql import SparkSession 
from pyspark.sql.types import StructType, StructField, IntegerType, LongType, DoubleType
import pandas as pd # Hanya jika Anda masih ingin membuat Pandas DF dulu

# Import relatif
from . import models_loader

# --- Pydantic Schemas ---
# ... (Skema Anda sudah benar, saya tidak akan salin ulang untuk menghemat ruang) ...
class HealthCheckResponse(BaseModel):
    status: str
    spark_session_active: bool
    models_loaded: List[str]
    warnings: List[str] = []

class RecommendationItem(BaseModel):
    itemid: int 
    rating: float

class RecommendationResponse(BaseModel):
    visitorid: int 
    recommendations: List[RecommendationItem]

class TransactionPredictionRequest(BaseModel):
    visitorid_to_identify: Union[int, str] = Field(..., example=12345, description="Original visitor ID for response identification")
    num_views: int = Field(..., example=10)
    num_addtocart: int = Field(..., example=2)
    distinct_items_interacted: int = Field(..., example=5)

class TransactionPredictionResponse(BaseModel):
    visitorid: Union[int, str]
    will_transact: bool
    probability: float

class UserSegmentationRequest(BaseModel):
    visitorid_to_identify: Union[int, str] = Field(..., example=67890, description="Original visitor ID for response identification")
    total_events: int = Field(..., example=25)
    total_views: int = Field(..., example=20)
    total_addtocart: int = Field(..., example=3)
    total_transactions: int = Field(..., example=1)
    view_ratio: float = Field(..., example=0.8)
    addtocart_ratio: float = Field(..., example=0.12)
    transaction_ratio: float = Field(..., example=0.05)

class UserSegmentationResponse(BaseModel):
    visitorid: Union[int, str]
    cluster_id: int

app = FastAPI(
    title="E-commerce Behavior API",
    description="API for product recommendations, transaction prediction, and user segmentation.",
    version="1.0.1" # Versi bisa Anda naikkan
)

# Tidak ada variabel spark global di sini lagi. models_loader akan mengelolanya.

@app.on_event("startup")
async def startup_event():
    print("API Service starting up...")
    # models_loader.load_all_models_on_startup() akan menginisialisasi SparkSession
    # dan memuat semua model ke dalam cache internal models_loader.
    models_loader.load_all_models_on_startup()
    
    # Verifikasi setelah startup
    spark_check = models_loader.get_spark_session()
    if spark_check and spark_check.sparkContext:
        print("SparkSession is active and model loading process completed.")
    else:
        print("CRITICAL: SparkSession could not be initialized or is not active post-startup. API may not function correctly.")

@app.on_event("shutdown")
async def shutdown_event():
    spark_check = models_loader.get_spark_session() # Dapatkan session yang ada
    if spark_check: # Hanya hentikan jika memang ada
        print("API Service shutting down. Stopping SparkSession...")
        spark_check.stop()
        print("SparkSession stopped.")

# Fungsi helper yang benar
def get_spark_and_model(model_name: str):
    """
    Mengambil SparkSession yang aktif dan model yang diminta dari models_loader.
    Akan raise HTTPException jika SparkSession atau model tidak tersedia.
    """
    spark = models_loader.get_spark_session() # Selalu ambil dari loader
    if not spark or not spark.sparkContext:
        # models_loader.load_all_models_on_startup() # Panggil lagi jika gagal
        # spark = models_loader.get_spark_session()
        # if not spark or not spark.sparkContext: # Cek lagi
        #     raise HTTPException(status_code=503, detail="Spark session is not available or inactive.")
        # Daripada mencoba load ulang di sini, lebih baik pastikan startup berhasil
        # atau health check akan menunjukkan masalah.
        raise HTTPException(status_code=503, detail="Spark session is not available or inactive. API may have failed to start correctly.")

    model = models_loader.get_loaded_model(model_name)
    if model is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model '{model_name}' is not available or failed to load. Check API startup logs."
        )
    return spark, model

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    spark = models_loader.get_spark_session() # Ambil dari loader
    models_status = []
    for model_name in ['recommender', 'transaction_predictor', 'user_segmentation']:
        if models_loader.get_loaded_model(model_name):
            models_status.append(model_name)
            
    return HealthCheckResponse(
        status="ok" if spark and spark.sparkContext else "degraded",
        spark_session_active=spark is not None and spark.sparkContext is not None,
        models_loaded=models_status,
        warnings=models_loader.get_model_load_warnings()
    )

@app.get("/recommendations/{visitorid_int}", response_model=RecommendationResponse)
async def get_recommendations_for_user(
    visitorid_int: int = FastApiPath(..., example=123, description="The integer ID of the visitor (visitorid_int)"),
    num_recommendations: int = Query(5, ge=1, le=20, example=3)
):
    spark, recommender_model = get_spark_and_model('recommender') # Menggunakan helper yang benar

    try:
        print(f"--- Generating recommendations for visitorid_int {visitorid_int} ---")
        user_df_for_als = spark.createDataFrame([(visitorid_int,)], [recommender_model.getUserCol()])
        # ... (sisa logika endpoint rekomendasi seperti yang sudah benar sebelumnya) ...
        user_recs_df = recommender_model.recommendForUserSubset(user_df_for_als, num_recommendations)
        raw_recs_row = user_recs_df.select("recommendations").first()
        recommendations_output = []
        if raw_recs_row and raw_recs_row.recommendations: 
            item_col_name = recommender_model.getItemCol() 
            for rec_row in raw_recs_row.recommendations:
                recommendations_output.append(
                    RecommendationItem(itemid=rec_row[item_col_name], rating=rec_row.rating)
                )
            print(f"Generated {len(recommendations_output)} recommendations for user {visitorid_int}.")
        else:
            print(f"No recommendations found for user {visitorid_int}.")
        return RecommendationResponse(visitorid=visitorid_int, recommendations=recommendations_output)

    except Exception as e:
        print(f"Error in recommendation endpoint for visitorid_int {visitorid_int}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Could not generate recommendations: {str(e)}")

@app.post("/predict-transaction", response_model=TransactionPredictionResponse)
async def predict_transaction(request_data: TransactionPredictionRequest):
    spark, predictor_model = get_spark_and_model('transaction_predictor') # Menggunakan helper yang benar
    try:
        # ... (logika Anda untuk membuat input_spark_df dari request_data) ...
        input_data = [(
            request_data.num_views, 
            request_data.num_addtocart, 
            request_data.distinct_items_interacted
        )]
        schema = StructType([
            StructField("num_views", LongType(), True),
            StructField("num_addtocart", LongType(), True),
            StructField("distinct_items_interacted", LongType(), True)
        ])
        input_spark_df = spark.createDataFrame(input_data, schema=schema)

        predictions_df = predictor_model.transform(input_spark_df)
        result = predictions_df.select("prediction", "probability").first()

        if not result:
            raise HTTPException(status_code=500, detail="Model did not return a transaction prediction.")

        probability_class_1 = float(result.probability[1])
        will_transact = bool(result.prediction == 1.0)
        return TransactionPredictionResponse(
            visitorid=request_data.visitorid_to_identify,
            will_transact=will_transact,
            probability=probability_class_1
        )
    except Exception as e:
        print(f"Error in transaction prediction endpoint for visitor {request_data.visitorid_to_identify}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Could not predict transaction: {str(e)}")

@app.post("/segment-user", response_model=UserSegmentationResponse)
async def segment_user(request_data: UserSegmentationRequest):
    spark, segmenter_model = get_spark_and_model('user_segmentation') # Menggunakan helper yang benar
    try:
        # ... (logika Anda untuk membuat input_spark_df dari request_data) ...
        input_data = [(
            request_data.total_events, request_data.total_views, request_data.total_addtocart,
            request_data.total_transactions, request_data.view_ratio, request_data.addtocart_ratio,
            request_data.transaction_ratio
        )]
        # Pastikan skema cocok dengan model Anda
        schema = StructType([
            StructField("total_events", LongType(), True),
            StructField("total_views", LongType(), True),
            StructField("total_addtocart", LongType(), True),
            StructField("total_transactions", LongType(), True),
            StructField("view_ratio", DoubleType(), True),
            StructField("addtocart_ratio", DoubleType(), True),
            StructField("transaction_ratio", DoubleType(), True)
        ])
        input_spark_df = spark.createDataFrame(input_data, schema=schema)

        segment_df = segmenter_model.transform(input_spark_df)
        result = segment_df.select("prediction").first()

        if not result:
            raise HTTPException(status_code=500, detail="Model did not return a user segment.")
            
        cluster_id = int(result.prediction)
        return UserSegmentationResponse(
            visitorid=request_data.visitorid_to_identify,
            cluster_id=cluster_id
        )
    except Exception as e:
        print(f"Error in user segmentation endpoint for visitor {request_data.visitorid_to_identify}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Could not segment user: {str(e)}")
