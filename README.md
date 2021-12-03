# TL-DR : Meaning based Korean Extractive Summarization

## 모델 소개
- TL-DR은 BERT를 이용한 한국어 문서 요약을 제공해줍니다. 기존의 [BertSum](https://github.com/nlpyang/BertSum) 모델을 다양한 한국어 BERT (SKT의 KoBERT, ESTI의 한국어 BERT 등)에 적용할 수 있도록 변형한 모델입니다.
- 실제 문서에서 주제 및 중요한 내용은 문장 단위 보다는 구절처럼 보다 작은 형태로 나타나는 점에 착안하여 형태소 단위로 쪼개 모델의 학습을 진행해봤습니다.
- 형태소 단위로 데이터를 받는 [KorBert](https://aiopen.etri.re.kr/service_dataset.php), 그리고 문장 단위로 데이터를 받는 [KoBert](https://github.com/SKTBrain/KoBERT)를 BERT 모델로 이용했고, 각각의 코드는 raqoon886님의 [Velog](https://velog.io/@raqoon886/KorBertSum-SummaryBot) 글과 uoneway님의 [KoBertSum](https://github.com/uoneway/KoBertSum) 를 참고해서 작성했습니다.
- 모델 학습 및 평가에 사용한 데이터는 AiHub에 공개된 [문서요약 텍스트](https://aihub.or.kr/aidata/8054)로, 각 모델의 ROGUE Score은 다음과 같이 나옵니다.


<table class="tg">
<thead>
  <tr>
    <th class="tg-0pky">Model</th>
    <th class="tg-0pky">ROUGE-1</th>
    <th class="tg-0pky">ROGUE-2</th>
    <th class="tg-0pky">ROGUE-L</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td class="tg-0pky">Vanilia BERT+Transformer</td>
    <td class="tg-0pky">24.12</td>
    <td class="tg-0pky">9.03</td>
    <td class="tg-0pky">23.07</td>
  </tr>
  <tr>
    <td class="tg-0pky">KoBert+Classifier</td>
    <td class="tg-0pky">24.97</td>
    <td class="tg-0pky">9.78</td>
    <td class="tg-0pky">23.91</td>
  </tr>
  <tr>
    <td class="tg-0pky">KoBert+Transformer</td>
    <td class="tg-0pky">22.66</td>
    <td class="tg-0pky">8.79</td>
    <td class="tg-0pky">21.68</td>
  </tr>
  <tr>
    <td class="tg-0pky">bert-kor-base+Transformer</td>
    <td class="tg-0pky">25.15</td>
    <td class="tg-0pky">9.82</td>
    <td class="tg-0pky">24.04</td>
  </tr>
  <tr>
    <td class="tg-0pky">KorBert+Classifier</td>
    <td class="tg-0pky">34.40</td>
    <td class="tg-0pky">13.82</td>
    <td class="tg-0pky">33.27</td>
  </tr>
</tbody>
</table>

<br><br>
![image](https://user-images.githubusercontent.com/78715821/142162348-8574ae84-98b0-43f3-aee0-e27eecad0548.png)

## 사용법

### 1. Preprocess
 - AIHub에서 원본 데이터를 다운받았다면, jsonl 파일을 불러와 csv 파일로 바꿔주는 과정이 필요합니다.
 완성된 csv 파일은 다음과 같은 형태로 저장되어 있어야 합니다.
 
 <table>
<thead>
  <tr>
    <th>media</th>
    <th>id</th>
    <th>article_original</th>
    <th>abstractive</th>
    <th>extractive</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>법률</td>
    <td>0</td>
    <td>['원고가 소속회사의...', '노조조합장이...']</td>
    <td>원고가 주동하여 회사업무...</td>
    <td>[5,4,2]</td>
  </tr>
  <tr>
    <td>신문기사</td>
    <td>1</td>
    <td>['이시형 터키 리라화 가치...', '자동차강판...']</td>
    <td>2009년 설립된 유럽...</td>
    <td>[1,2,4]</td>
  </tr>
</tbody>
</table>
 
  - 처리가 완료된 csv 파일을 이용해 ```/src/preprocess.ipynb``` 를 이용해 json 파일로 저장해주면 됩니다. 이때 카카오의 [khaiii](https://github.com/kakao/khaiii) 형태소 분석기의 설치가 필요합니다. 
  - 완성된 json 파일에 대해 BERT의 input token으로 임베딩을 진행해주기 위해 다음과 같은 코드를 실행해줍니다.
 ```
 python preprocess.py -mode format_to_bert -raw_path ../json_data -save_path ../bert_data
 ```
 
 ### 2. Train and Test
  - 모델 훈련을 시작하기 전에, ETRI 사이트에서 KorBERT 사용 허가를 받아야 합니다. 허가를 받았다면, 첫번째 모델을 다운받아 /content/ETRIBert 폴더에 압축을 풀어주면 됩니다.
  - Train / Validation / Test 모두 /src/train.py를 이용해 실행되게 됩니다.
  - 아래 코드는 Classifier을 이용해 학습시키는 코드 예시입니다. 자세한 파라미터 세팅은 documentation.pdf에 적혀있습니다.
  ```
  python train.py -mode train -encoder classifier -dropout 0.1 -bert_data_path ../bert_data/korean -model_path ../models/ -lr 2e-3 -visible_gpus 0 -gpu_ranks 0 -world_size 1 -report_every 50 -save_checkpoint_steps 1000 -batch_size 2000 -decay_method noam -train_steps 30000 -accum_count 1 -log_file ../logs/training_log.txt -use_interval true -warmup_steps 6000 -bert_model ../content/ETRIBert -bert_config_path ../content/ETRIBert/bert_config.json -temp_dir ./temp
  ```
  - 실제 모델 학습 및 테스트의 과정은 /src/train.ipynb에 작성되어 있습니다. 테스트를 진행하기 위해서는 /models/model_builder.py 파일에서 ``` # for test only ```로 주석처리된 부분을 해제하고 실행해야만 합니다.
