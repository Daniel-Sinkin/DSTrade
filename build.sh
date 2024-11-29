python3 "util/av_doc_to_integration_api.py"
python3 "util/av_doc_to_tests.py"

ruff format "src/av_integration_api.py" 
ruff format "tests/test_av_integration_api.py" 
ruff clean