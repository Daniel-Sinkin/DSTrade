python3 "util/av_doc_to_integration.py"
python3 "util/av_doc_to_tests.py"

ruff format "src/av_integration.py" 
ruff format "tests/test_av_integration.py" 
ruff clean