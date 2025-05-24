import os
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, when, count, countDistinct, sum as _sum, lit, avg, max as _max
from pyspark.sql.types import IntegerType, LongType, StringType, StructType, StructField
from pyspark.ml.feature import StringIndexer, VectorAssembler, StandardScaler
from pyspark.ml.recommendation import ALS
from pyspark.ml.classification import LogisticRegression, RandomForestClassifier
from pyspark.ml.clustering import KMeans
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import ClusteringEvaluator # Untuk KMeans

def get_spark_session(app_name="RetailRocketSparkApp"):
    """Membuat atau mendapatkan SparkSession yang sudah ada."""
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .getOrCreate()
    return spark

def load_and_merge_batches(spark: SparkSession, base_path: str, start_batch_num: int, end_batch_num: int, file_prefix: str = "batch_") -> DataFrame:
    """Membaca beberapa file batch CSV dan menggabungkannya menjadi satu Spark DataFrame."""
    all_dfs = []
    print(f"Loading batches from {start_batch_num} to {end_batch_num} with prefix '{file_prefix}'...") # Menambahkan prefix ke log

    schema = StructType([
        StructField("timestamp", LongType(), True),
        StructField("visitorid", IntegerType(), True),
        StructField("event", StringType(), True),
        StructField("itemid", IntegerType(), True),
        StructField("transactionid", LongType(), True)
    ])

    for i in range(start_batch_num, end_batch_num + 1):
        file_name = f"{file_prefix}{i:03d}.csv"
        file_path = os.path.join(base_path, file_name)

        if os.path.exists(file_path):
            try:
                df_batch = spark.read.csv(file_path, header=True, schema=schema)
                all_dfs.append(df_batch)
            except Exception as e:
                print(f"Warning: Could not load or process {file_path}. Error: {e}")
        else:
            print(f"Warning: File {file_path} not found.")

    if not all_dfs:
        print("No dataframes loaded. Returning empty DataFrame with defined schema.")
        return spark.createDataFrame([], schema)

    if len(all_dfs) == 1:
        merged_df = all_dfs[0]
    else:
        merged_df = all_dfs[0]
        # Menggunakan variabel loop yang berbeda (idx) agar tidak bentrok dengan 'i' dari loop luar
        for idx in range(1, len(all_dfs)):
            merged_df = merged_df.unionByName(all_dfs[idx])
    
    if merged_df.head(1):
        print(f"Total rows after merging batches {start_batch_num}-{end_batch_num}: {merged_df.count()}")
    else:
        print(f"Merged DataFrame for batches {start_batch_num}-{end_batch_num} is empty.")
    return merged_df

def train_recommender_model(spark: SparkSession, df: DataFrame, model_path: str):
    print("\n--- Training Recommender Model (ALS) ---")
    df_filtered = df.filter(col("event").isin(["view", "addtocart", "transaction"])) \
                    .filter(col("visitorid").isNotNull() & col("itemid").isNotNull())

    df_processed = df_filtered.withColumn("visitorid_int", col("visitorid").cast(IntegerType())) \
                              .withColumn("itemid_int", col("itemid").cast(IntegerType()))

    df_ratings = df_processed.withColumn("rating",
        when(col("event") == "view", 1.0)
        .when(col("event") == "addtocart", 3.0)
        .when(col("event") == "transaction", 5.0)
        .otherwise(0.0)
    ).select("visitorid_int", "itemid_int", "rating")

    df_ratings = df_ratings.filter(col("rating") > 0)
    
    if df_ratings.head(1):
        df_ratings.cache()
        print(f"Data for ALS training: {df_ratings.count()} ratings.")
    else:
        print("No data available for ALS training after filtering. Skipping.")
        return

    als = ALS(userCol="visitorid_int", itemCol="itemid_int", ratingCol="rating",
              coldStartStrategy="drop",
              nonnegative=True,
              implicitPrefs=False,
              regParam=0.1,
              rank=10)

    print("Training ALS model...")
    model = als.fit(df_ratings)

    print(f"Saving ALS model to {model_path}")
    model.write().overwrite().save(model_path)
    print("Recommender model saved.")
    df_ratings.unpersist()

def train_transaction_predictor_model(spark: SparkSession, df: DataFrame, model_path: str):
    print("\n--- Training Transaction Predictor Model (Logistic Regression/Random Forest) ---")
    visitor_features = df.groupBy("visitorid").agg(
        count(when(col("event") == "view", 1)).alias("num_views"),
        count(when(col("event") == "addtocart", 1)).alias("num_addtocart"),
        countDistinct("itemid").alias("distinct_items_interacted"),
        _max(when(col("event") == "transaction", 1).otherwise(0)).alias("has_transaction")
    ).na.fill(0)

    if not visitor_features.head(1):
        print("No data available for transaction predictor after aggregation. Skipping.")
        return
        
    visitor_features.cache()
    print(f"Data for Transaction Predictor: {visitor_features.count()} visitors.")

    feature_cols = ["num_views", "num_addtocart", "distinct_items_interacted"]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features_unscaled")
    scaler = StandardScaler(inputCol="features_unscaled", outputCol="features", withStd=True, withMean=True)
    
    rf = RandomForestClassifier(featuresCol="features", labelCol="has_transaction", numTrees=50, maxDepth=5)
    pipeline = Pipeline(stages=[assembler, scaler, rf])

    print("Training transaction predictor model...")
    model = pipeline.fit(visitor_features)

    print(f"Saving transaction predictor model to {model_path}")
    model.write().overwrite().save(model_path)
    print("Transaction predictor model saved.")
    visitor_features.unpersist()

def train_user_segmentation_model(spark: SparkSession, df: DataFrame, model_path: str):
    print("\n--- Training User Segmentation Model (KMeans) ---")
    user_behavior = df.groupBy("visitorid").agg(
        count("*").alias("total_events"),
        _sum(when(col("event") == "view", 1).otherwise(0)).alias("total_views"),
        _sum(when(col("event") == "addtocart", 1).otherwise(0)).alias("total_addtocart"),
        _sum(when(col("event") == "transaction", 1).otherwise(0)).alias("total_transactions")
    ).na.fill(0)

    user_behavior = user_behavior.withColumn(
        "view_ratio",
        when(col("total_events") > 0, col("total_views") / col("total_events")).otherwise(0)
    ).withColumn(
        "addtocart_ratio",
        when(col("total_events") > 0, col("total_addtocart") / col("total_events")).otherwise(0)
    ).withColumn(
        "transaction_ratio",
        when(col("total_views") > 0, col("total_transactions") / col("total_views")).otherwise(0)
    )

    if not user_behavior.head(1):
        print("No data available for user segmentation after aggregation. Skipping.")
        return

    user_behavior.cache()
    print(f"Data for User Segmentation: {user_behavior.count()} users.")

    feature_cols_segment = ["total_events", "total_views", "total_addtocart", "total_transactions", "view_ratio", "addtocart_ratio", "transaction_ratio"]
    assembler_segment = VectorAssembler(inputCols=feature_cols_segment, outputCol="features_unscaled", handleInvalid="skip")
    scaler_segment = StandardScaler(inputCol="features_unscaled", outputCol="features", withStd=True, withMean=True)
    kmeans = KMeans(featuresCol="features", k=5, seed=1)
    pipeline_segment = Pipeline(stages=[assembler_segment, scaler_segment, kmeans])

    print("Training KMeans model...")
    model = pipeline_segment.fit(user_behavior)

    print(f"Saving KMeans model to {model_path}")
    model.write().overwrite().save(model_path)
    print("User segmentation model saved.")
    user_behavior.unpersist()

def main():
    spark = get_spark_session()

    base_data_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed_batches")
    model_base_path = os.path.join(os.path.dirname(__file__), "models")

    # --- Model 1: Recommender ---
    print("Processing Model 1: Recommender")
    df_model1 = load_and_merge_batches(spark, base_data_path, 1, 50) # Akan mencari batch_001.csv hingga batch_050.csv
    if df_model1.head(1):
        train_recommender_model(spark, df_model1, os.path.join(model_base_path, "recommender_model_v1"))
    else:
        print("Skipping Recommender model training due to no data loaded for model 1.")

    # --- Model 2: Transaction Predictor ---
    print("\nProcessing Model 2: Transaction Predictor")
    df_model2 = load_and_merge_batches(spark, base_data_path, 51, 100) # Akan mencari batch_051.csv hingga batch_100.csv
    if df_model2.head(1):
        train_transaction_predictor_model(spark, df_model2, os.path.join(model_base_path, "transaction_predictor_model_v1"))
    else:
        print("Skipping Transaction Predictor model training due to no data loaded for model 2.")

    # --- Model 3: User Segmentation ---
    print("\nProcessing Model 3: User Segmentation")
    df_model3 = load_and_merge_batches(spark, base_data_path, 101, 150) # Akan mencari batch_101.csv hingga batch_150.csv
    if df_model3.head(1):
        train_user_segmentation_model(spark, df_model3, os.path.join(model_base_path, "user_segmentation_model_v1"))
    else:
        print("Skipping User Segmentation model training due to no data loaded for model 3.")

    print("\nAll models processed.")
    spark.stop()

if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    model_output_dir = os.path.join(current_dir, "models")
    
    os.makedirs(os.path.join(model_output_dir, "recommender_model_v1"), exist_ok=True)
    os.makedirs(os.path.join(model_output_dir, "transaction_predictor_model_v1"), exist_ok=True)
    os.makedirs(os.path.join(model_output_dir, "user_segmentation_model_v1"), exist_ok=True)
    main()