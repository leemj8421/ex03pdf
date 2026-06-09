import re
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# ==========================================
# 1. 핵심 함수 정의 (기존과 거의 동일합니다)
# ==========================================
def extract_video_id(url):
    """유튜브 URL에서 11자리 비디오 ID를 추출합니다."""
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_video_transcript(video_id):
    """비디오 ID를 사용해 영상의 자막을 가져옵니다."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'ko'])
        full_text = " ".join([entry['text'] for entry in transcript])
        return full_text
    except Exception as e:
        return f"에러: {e}"

def summarize_and_translate(text, api_key):
    """AI를 사용해 텍스트를 요약하고 번역합니다."""
    # 입력받은 API 키로 인증 설정
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    다음 텍스트는 유튜브 영상의 전체 자막입니다. 
    이 내용을 바탕으로 영상의 핵심 내용을 파악하기 쉽게 3~5가지 불릿 포인트로 요약하고, 
    모든 결과를 자연스러운 한국어로 번역해서 알려주세요.

    자막 내용:
    {text}
    """
    response = model.generate_content(prompt)
    return response.text

# ==========================================
# 2. 웹페이지(UI) 구성
# ==========================================
# 웹 브라우저 탭의 제목과 아이콘을 설정합니다.
st.set_page_config(page_title="유튜브 AI 요약기", page_icon="🎬")

# 메인 화면 제목
st.title("🎬 유튜브 영상 요약 및 번역기")
st.write("유튜브 링크만 넣으면 AI가 핵심 내용을 요약하고 번역해 줍니다!")

# 좌측 사이드바 구성 (API 키 입력란)
with st.sidebar:
    st.header("⚙️ 설정")
    # type="password"를 사용해 입력한 키가 가려지게 만듭니다.
    user_api_key = st.text_input("Gemini API 키를 입력하세요:", type="password")
    st.info("💡 API 키는 구글 AI 스튜디오에서 무료로 발급받을 수 있습니다.")

# 메인 화면 링크 입력란
youtube_url = st.text_input("🔗 요약할 유튜브 링크를 붙여넣으세요:")

# 버튼을 눌렀을 때 실행될 동작
if st.button("요약 시작!"):
    # 1. 예외 처리: API 키나 링크가 없는 경우 경고 메시지를 띄웁니다.
    if not user_api_key:
        st.warning("👈 왼쪽 사이드바에 Gemini API 키를 먼저 입력해 주세요!")
    elif not youtube_url:
        st.warning("유튜브 링크를 입력해 주세요!")
    else:
        # 2. 로딩 애니메이션 띄우기
        with st.spinner("영상을 분석하고 요약하는 중입니다... 잠시만 기다려주세요 ⏳"):
            
            # 3. 단계별 작업 수행
            video_id = extract_video_id(youtube_url)
            
            if video_id:
                transcript_text = get_video_transcript(video_id)
                
                # 자막을 성공적으로 가져왔는지 확인
                if "에러:" not in transcript_text:
                    try:
                        # 요약 실행
                        final_result = summarize_and_translate(transcript_text, user_api_key)
                        
                        # 결과 출력
                        st.success("요약이 완료되었습니다! 🎉")
                        st.markdown("### 📝 요약 결과")
                        st.write(final_result)
                        
                    except Exception as e:
                        st.error(f"AI 요약 중 오류가 발생했습니다. API 키를 확인해 주세요. (상세 에러: {e})")
                else:
                    st.error("자막을 추출할 수 없습니다. 자막이 없는 영상이거나 제한된 영상일 수 있습니다.")
            else:
                st.error("유효한 유튜브 링크가 아닙니다. 링크를 다시 확인해 주세요.")