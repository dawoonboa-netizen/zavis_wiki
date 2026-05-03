import speech_recognition as sr
import pyttsx3

# Text-to-Speech 엔진 설정
engine = pyttsx3.init()
voices = engine.getProperty('voices')
# 원하는 목소리 설정 (시스템에 따라 인덱스 변경 필요)
engine.setProperty('voice', voices[0].id)

def speak(text):
    """텍스트를 음성으로 출력합니다."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """마이크 입력을 받아 텍스트로 변환합니다."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("듣는 중... 명령을 말씀해주세요.")
        r.pause_threshold = 1
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("시간 초과. 아무 말도 듣지 못했습니다.")
            return None

    try:
        print("음성 인식 중...")
        # Google Speech Recognition 사용
        command = r.recognize_google(audio, language='ko-KR')
        print(f"사용자 입력: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("음성 인식이 실패했습니다. 음성 입력이 명확하지 않습니다.")
        return None
    except sr.RequestError:
        print("인터넷 연결 오류. 음성 인식을 위해 인터넷 연결을 확인해주세요.")
        return None

if __name__ == "__main__":
    speak("J.A.R.V.I.S. 시스템이 활성화되었습니다. 무엇을 도와드릴까요?")
    
    while True:
        command = listen()
        
        if command:
            if "종료해" in command or "나가" in command:
                speak("시스템을 종료합니다. 안녕히 계세요.")
                break
            
            elif "시간" in command:
                import datetime
                now = datetime.datetime.now().strftime("%H시 %M분")
                speak(f"현재 시간은 {now}입니다.")
            
            elif "안녕" in command or "하이" in command:
                speak("안녕하세요! 무엇을 도와드릴까요?")
            
            else:
                speak("죄송하지만, 이해하지 못했습니다. 다시 명령해주세요.")

print("J.A.R.V.I.S. 종료.")