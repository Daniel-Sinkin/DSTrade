python3 "util/av_doc_to_integration.py"
python3 "util/av_doc_to_tests.py"

ruff format "util/av_integration_generated.py" 
ruff format "util/test_av_integration_generated.py" 
ruff clean