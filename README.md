# TL-DR : Korean Text Extractive Summarization

## 모델 소개
- TL-DR은 BERT를 이용한 한국어 문서 요약을 제공해줍니다. 기존의 [BertSum](https://github.com/nlpyang/BertSum) 모델을 다양한 한국어 BERT (SKT의 KoBERT, ESTI의 한국어 BERT 등)에 적용할 수 있도록 변형한 모델입니다.
- 모델 학습 및 평가에 사용한 데이터는 AiHub에 공개된 [문서요약 텍스트](https://aihub.or.kr/aidata/8054)로, 각 모델의 ROGUE Score은 다음과 같이 나옵니다.
<br><br>
![image](https://user-images.githubusercontent.com/78715821/142162348-8574ae84-98b0-43f3-aee0-e27eecad0548.png)

## 사용법
```
python install requirements.txt
```
