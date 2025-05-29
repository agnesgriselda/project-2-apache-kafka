# api_services/models_loader.py
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel # Pastikan ini diimpor jika model recommender adalah ALSModel
from pyspark.ml.pipeline import PipelineModel
import os
import tempfile

_spark_session_singleton = None
_loaded_models_cache = {}
_model_load_warnings = []

# Path DI DALAM KONTAINER tempat model dari host akan di-mount
# Ini harus konsisten dengan konfigurasi 'volumes' di docker-compose.api.yml
CONTAINER_MODEL_BASE_PATH = "/opt/spark/models_mounted" # Ini path target di dalam kontainer

def get_spark_session():
    global _spark_session_singleton
    if _spark_session_singleton is None:
        print("Initializing SparkSession for API (inside Docker)...")
        try:
            spark_local_dir_container = tempfile.mkdtemp(prefix="spark_local_api_")
            print(f"API Spark (Docker) using local directory: {spark_local_dir_container}")

            # Siapkan path dengan forward slashes terlebih dahulu
            java_io_tmpdir_path = spark_local_dir_container.replace("\\", "/")

            _spark_session_singleton = SparkSession.builder \
                .appName("ECommerceAPI_Docker") \
                .master("local[*]") \
                .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
                .config("spark.driver.memory", "2g") \
                .config("spark.executor.memory", "2g") \
                .config("spark.python.worker.faulthandler.enabled", "true") \
                .config("spark.local.dir", java_io_tmpdir_path) \
                .config("spark.driver.extraJavaOptions", f"-Djava.io.tmpdir={java_io_tmpdir_path}") \
                .config("spark.executor.extraJavaOptions", f"-Djava.io.tmpdir={java_io_tmpdir_path}") \
                .getOrCreate()
            print("SparkSession initialized (inside Docker).")
        except Exception as e:
            error_msg = f"FATAL: Could not initialize SparkSession (inside Docker): {e}"
            print(error_msg)
            _model_load_warnings.append(error_msg)
            raise RuntimeError(error_msg) from e
    return _spark_session_singleton

def _load_model_from_path(spark, model_class, path, model_type_name):
    if not os.path.exists(path): # 'path' di sini adalah path lengkap di dalam kontainer
        warning_msg = f"Model '{model_type_name}' not found at container path '{path}'. This endpoint will not work."
        print(f"WARNING: {warning_msg}")
        _model_load_warnings.append(warning_msg)
        return None
    try:
        print(f"Loading '{model_type_name}' model from container path '{path}'...")
        model = model_class.load(path) # Gunakan 'path' langsung
        print(f"'{model_type_name}' model loaded successfully.")
        return model
    except Exception as e:
        error_msg = f"Error loading '{model_type_name}' model from container path '{path}': {e}"
        print(f"ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        _model_load_warnings.append(error_msg)
        return None

def load_all_models_on_startup():
    global _loaded_models_cache, _model_load_warnings
    _model_load_warnings = []
    
    print("Attempting to load all models on API startup...")
    spark = get_spark_session()
    if not spark:
        _model_load_warnings.append("SparkSession failed to initialize. No models were loaded.")
        print("CRITICAL: Aborting model loading due to SparkSession initialization failure.")
        return

    # Menggunakan CONTAINER_MODEL_BASE_PATH yang didefinisikan di atas
    model_definitions = {
        'recommender': (ALSModel, os.path.join(CONTAINER_MODEL_BASE_PATH, "recommender_model_v1"), "Recommender (ALS)"),
        'transaction_predictor': (PipelineModel, os.path.join(CONTAINER_MODEL_BASE_PATH, "transaction_predictor_model_v1"), "Transaction Predictor"),
        'user_segmentation': (PipelineModel, os.path.join(CONTAINER_MODEL_BASE_PATH, "user_segmentation_model_v1"), "User Segmentation")
    }
    
    models_loaded_count = 0
    for name, (model_class, model_path_in_container, type_name) in model_definitions.items():
        model_instance = _load_model_from_path(spark, model_class, model_path_in_container, type_name)
        _loaded_models_cache[name] = model_instance
        if model_instance:
            models_loaded_count += 1
            
    if models_loaded_count == 0:
        print("CRITICAL WARNING: No models were successfully loaded. API endpoints will likely fail.")
    # ... (sisa fungsi sama) ...

def get_loaded_model(model_name: str):
    return _loaded_models_cache.get(model_name)

def get_model_load_warnings():
    return _model_load_warnings
