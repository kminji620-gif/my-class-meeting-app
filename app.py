import streamlit as st
import google.generativeai as genai
import random

st.set_page_config(page_title="5학년 질문 회의 생성기", layout="centered")

api_key = st.secrets.get("gemini_api_key")

st.markdown("""
<style>
    .script-box { background-color: #ffffff; border: 2px solid #e1e4e8; padding: 25px; border-radius: 15px; line-height: 2.0; font-size: 1.1rem; }
    .moderator { color: #1A5276; font-weight: bold; border-left: 4px solid #1A5276; padding-left: 10px; }
    .student1 { color: #C0392B; font-weight: bold; }
    .student2 { color: #1E8449; font-weight: bold; }
    .student3 { color: #7D3C98; font-weight: bold; }
    .student_gen { color: #6E2C00; font-weight: bold; }
    .tag_intent { background-color: #EBF5FB; color: #2874A6; padding: 2px 8px; border-radius: 10px; font-size: 0.85rem; border: 1px solid #AED6F1; margin-right: 5px; }
    .tag_clarify { background-color: #EAFAF1; color: #1D8348; padding: 2px 8px; border-radius: 10px; font-size: 0.85rem; border: 1px solid #ABEBC6; margin-right: 5px; }
    .tag_alt { background-color: #FEF9E7; color: #9A7D0A; padding: 2px 8px; border-radius: 10px; font-size: 0.85rem; border: 1px solid #F9E79F; margin-right: 5px; }
</style>
""", unsafe_allow_html=True)

if not api_key:
    st.error("⚠️ Secrets에 'gemini_api_key'를 등록해주세요.")
    st.stop()

# 모델 설정 (안정적인 버전)
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

RECOMMENDED_TOPICS = ["급식실 잔반 줄이기", "현장체험학습 장소 정하기", "복도 우측통행 규칙", "학급 장기자랑 종목 정하기"]

st.title("🏫 5학년 질문 회의 대본 생성기")
with st.sidebar:
    if st.button("💡 주제 추천"):
        st.session_state.topic_input = random.choice(RECOMMENDED_TOPICS)
    topic = st.text_input("주제", value=st.session_state.get('topic_input', ''))
    count = st.slider("인원", 3, 24, 4)

def get_speaker_class(name):
    if "사회자" in name: return "moderator"
    if "학생 1" in name: return "student1"
    if "학생 2" in name: return "student2"
    if "학생 3" in name: return "student3"
    return "student_gen"

def replace_tags(text):
    text = text.replace("[의도 파악]", '<span class="tag_intent">💬 의도 파악</span>')
    text = text.replace("[의미 명료화]", '<span class="tag_clarify">❓ 의미 명료화</span>')
    text = text.replace("[대안 탐색]", '<span class="tag_alt">💡 대안 탐색</span>')
    return text

if st.button("🚀 대본 생성하기", use_container_width=True):
    if not topic:
        st.warning("주제를 입력해 주세요.")
    else:
        with st.spinner("AI가 대본을 작성 중..."):
            try:
                prompt = f"초등 5학년 회의 대본. 주제: {topic}, 인원: {count}명. 서로 존댓말 사용. [의도 파악], [의미 명료화], [대안 탐색] 질문을 대사 앞에 포함할 것. '이름: [질문유형] 대사' 형식으로 써줘."
                response = model.generate_content(prompt)
                full_html = '<div class="script-box">'
                for line in response.text.split('\n'):
                    if ':' in line:
                        name, speech = line.split(':', 1)
                        full_html += f'<p><span class="{get_speaker_class(name)}">{name.strip()}:</span> {replace_tags(speech)}</p>'
                    else:
                        full_html += f'<p>{replace_tags(line)}</p>'
                full_html += '</div>'
                st.markdown(full_html, unsafe_allow_html=True)
                st.download_button("📂 저장", response.text, file_name="meeting.txt")
            except Exception as e:
                st.error(f"오류 발생: {e}")
