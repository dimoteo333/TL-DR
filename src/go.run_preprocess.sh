python preprocess.py \
    -mode format_to_bert \
    -raw_path ../json_data \
    -save_path ../bert_data \
    -vocab_file_path ../content/ETRIBert/vocab.korean_morp.list \

## TTAMorph.ipynb 파일을 통해 AIHub의 데이터 whole_data.csv의
## 전처리가 진행되어 json_data에 저장되어 있어야 한다
## json_data를 bert의 데이터 *.pt로 저장한다