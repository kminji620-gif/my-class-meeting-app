import streamlit as st
import google.generativeai as genai
import random

# 1. 페이지 설정 (반드시 가장 처음에 와야 합니다!)
st.set_page_config(page_title="5학년 질문 회의 생성기", layout="centered")

# 2. API 키 설정 (Secrets에서 가져오기)
api_key = st.secrets.get("AIzaSyC7cIyLGPan-7M-WsFzsxE-fSOVOL8IFxw")

# 3. CSS 스타일 정의 (색상 및 디자인)
st.markdown("""
<style>
    .script-box {
        background-color: #ffffff;
        border: 2px solid #e1e4e8;
        padding: 25px;
        border-radius: 15px;
        line-height: 2.0;
        font-size: 1.1rem;
    }
    .moderator { color: #1A5276; font-weight: bold; border-left: 4px solid #1A5276; padding-left: 10px; }
    .student1 { color: #C0392B; font-weight: bold; }
    .student2 { color: #1E8449; font-weight: bold; }
    .student3 { color: #7D3C98; font-weight: bold; }
    .student_gen { color: #6E2C00; font-weight: bold; }
    
    .tag_intent { background-color: #EBF5FB; color: #2874A6; padding: 2px 8px; border-radius: 10px; font-size: 0.85rem; border: 1px solid #AED6F1; }
    .tag_clarify { background-color: #EAFAF1; color: #1D8348; padding: 2px 8px; border-radius: 10px; font-size: 0.85rem; border: 1px solid #ABEBC6; }
    .tag_alt { background-color: #FEF9E7; color: #9A7D0A; padding: 2px 8px; border-radius: 10px; font-size: 0.85rem; border: 1px solid #F9E79F; }
</style>
""", unsafe_allow_with_html=True)

# API 키 체크
if not api_key:
    st.error("⚠️ [설정 필요] Streamlit Cloud의 Settings > Secrets에 'gemini_api_key'를 등록해주세요.")
    st.stop()

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"API 연결 오류: {e}")
    st.stop()

# 4. 추천 주제 리스트
RECOMMENDED_TOPICS = [
    "급식실 잔반을 줄이기 위한 우리 반 실천 방안",
    "현장체험학습 장소 결정하기 (박물관 vs 테마파크)",
    "복도 우측통행을 즐겁게 실천하는 방법",
    "학급 장기자랑의 종목과 순서 정하기",
    "스마트폰 사용 시간을 줄이는 우리만의 약속",
    "쉬는 시간 교실 놀이 기구 사용 규칙"
]

# 5. UI 구성
st.title("🏫 5학년 질문 회의 대본 생성기")
st.caption("상대의 말을 듣고 질문하며 해결책을 찾아가는 연습")

with st.sidebar:
    st.header("⚙️ 설정")
    if st.button("💡 주제 추천받기"):
        st.session_state.topic_input = random.choice(RECOMMENDED_TOPICS)
    
    topic = st.text_input("회의 주제", 
                         value=st.session_state.get('topic_input', ''),
                         placeholder="주제를 입력하세요.")
    
    count = st.slider("참여 인원 (사회자 포함)", 3, 24, 4)

# 텍스트 변환 함수들
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

# 6. 생성 버튼 및 로직
if st.button("🚀 대본 생성하기", use_container_width=True):
    if not topic:
        st.warning("주제를 입력해 주세요.")
    else:
        with st.spinner("AI 친구가 대본을 쓰고 있어요..."):
            prompt = f"""
            초등학교 5학년 수준의 회의 대본을 써줘. 
            주제: {topic}, 인원: {count}명(사회자, 학생 1, 학생 2... 순서)
            규칙:
            1. 서로 존댓말 사용하기.
            2. 앞 사람의 말을 요약하며 질문하기.
            3. [의도 파악], [의미 명료화], [대안 탐색] 질문을 대사 앞에 반드시 포함할 것.
            형식: '이름: [질문유형] 대사' 형태로 작성해줘.
            """
            
            try:
                response = model.generate_content(prompt)
                full_html = '<div class="script-box">'
                
                for line in response.text.split('\n'):
                    if ':' in line:
                        name, speech = line.split(':', 1)
                        cls = get_speaker_class(name)
                        speech = replace_tags(speech)
                        full_html += f'<p><span class="{cls}">{name.strip()}:</span> {speech.strip()}</p>'
                    else:
                        full_html += f'<p>{replace_tags(line)}</p>'
                
                full_html += '</div>'
                st.markdown(full_html, unsafe_allow_with_html=True)
                st.download_button("📂 대본 저장", response.text, file_name="meeting.txt")
            except Exception as e:
                st.error(f"생성 실패: {e}")
