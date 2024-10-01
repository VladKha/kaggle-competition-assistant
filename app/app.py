import hashlib
import os
import io
import time
import uuid
import logging
import base64
import joblib

import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from streamlit_free_text_select import st_free_text_select
from audiorecorder import audiorecorder

from faster_whisper import WhisperModel
from melo.api import TTS


from dotenv import load_dotenv
load_dotenv()

from assistant import ask_assistant #, speech_to_text
from db import save_conversation, save_feedback, get_recent_conversations, get_feedback_stats

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__file__)


COMPETITION_2_SLUG = {
    'LLM Zoomcamp 2024 Competition (15 Sep 2024 snapshot)': 'llm-zoomcamp-2024-competition',
    'ARC Prize 2024 (30 Oct 2024 snapshot)': 'arc-prize-2024',
    'Rohlik Orders Forecasting Challenge (15 Sep 2024 snapshot)': 'rohlik-orders-forecasting-challenge',
}
SEARCH_TYPES_DICT = {
    'Lexical': 'lexical',
    'Semantic': 'semantic',
    'Hybrid + RRF reranking': 'hybrid_rff'
}

@st.cache_resource
def init_assistants():
    return joblib.load('assistants.pkl')

@st.cache_resource
def load_audio_models(model_size="large-v3"):
    # model_size = 'distil-large-v3'
    stt_model = WhisperModel(model_size, device="auto", compute_type="int8")
    tts_model = TTS(language='EN', device='auto')
    return stt_model, tts_model


def hash_bytesio(bytesio_object):
    bytesio_object.seek(0)  # Ensure we're at the start of the stream
    sha256 = hashlib.sha256()
    for chunk in iter(lambda: bytesio_object.read(4096), b''):
        sha256.update(chunk)
    return sha256.hexdigest()


def speech_to_text(model, audio):
    logger.info('Translating speech to text...')
    start = time.time()

    # check cache
    cache_file_name = 'cache_stt.pkl'
    if os.path.exists(cache_file_name):
        cache = joblib.load(cache_file_name)
    else:
        cache = {}

    audio_hash = hash_bytesio(io.BytesIO(audio))
    if audio_hash in cache:
        text = cache[audio_hash]
        logger.info(f'Found audio in cache - loading transcription from cache...')
    else:
        segments, info = model.transcribe(io.BytesIO(audio), beam_size=3)
        # print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
        text = ''
        for segment in segments:
            # print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            text += segment.text

    # store in cache
    cache[audio_hash] = text
    with open(cache_file_name, 'wb') as f:
        joblib.dump(cache, f)

    end = time.time()
    logger.info(f'Speech to text completed in {end - start:.2f} seconds.')
    return text.strip()


def text_to_speech(text, result_file_path='result.wav'):
    logger.info('Translating text to speech...')
    start = time.time()
    speaker_ids = tts_model.hps.data.spk2id
    tts_model.tts_to_file(text, speaker_ids['EN-US'], result_file_path, speed=1.2)
    end = time.time()
    logger.info(f'Text to speech completed in {end - start:.2f} seconds. Result saved in {result_file_path}')


# didn't work because required to provide docker access to host audio device, which was cumbersome
# def play_audio(file_path):
#     from pydub import AudioSegment
#     from pydub.playback import play
#     logger.info(f'Playing audio from {file_path}')
#     sound = AudioSegment.from_wav(file_path)
#     play(sound)
#     logger.info('Audio playback completed')


def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


def create_ui():
    # Session state initialization
    if 'current_question_id' not in st.session_state:
        st.session_state.current_question_id = -1
    if 'count' not in st.session_state:
        st.session_state.count = 0
        logger.info("Feedback count initialized to 0")

    # Page header
    logger.info("Starting the Kaggle Assistant application")
    st.markdown(
        """
        <h1 style="display: flex; align-items: center;">
            <img src="data:image/png;base64,{}" width="180" height="60" style="margin-right: 10px;">
            Competition Assistant
        </h1>
        """.format(get_base64_image('kaggle_icon.png')),
        unsafe_allow_html=True
    )
    st.text("Ask questions about a Kaggle competition")
    competition = st.selectbox(
        "Select competition:",
        list(COMPETITION_2_SLUG.keys())
    )
    logger.info(f"User selected competition: {competition}")

    # retrieval configs
    col1, col2 = st.columns([2, 1])
    with col1:
        search_type = st.radio(
            "Select retrieval type:",
            ["Lexical", "Semantic", "Hybrid + RRF reranking"],
            index=2
        )
        logger.info(f"User selected retrieval type: {search_type}")
    with col2:
        retrieval_n_results = st.slider(
            "Number of retrieved documents for context",
            min_value=1,
            max_value=20,
            step=1,
            value=10
        )
        logger.info(f"Slider value: {retrieval_n_results}")

    # question input
    col1, col2 = st.columns([0.55,0.45])
    with col2:
        st.write('<div style="padding-top: 20px;"></div>', unsafe_allow_html=True)
        audio = audiorecorder(start_prompt="", stop_prompt="", pause_prompt="", show_visualizer=False, key='question_recorder')
        audio_question = None
        if len(audio) > 0:
            audio_record = audio.export().read()
            audio_question = speech_to_text(stt_model, audio_record)
            # audio_question = speech_to_text(audio)
    with col1:
        questions_options = [
            'What is the competition about?',
            'What are competition prizes?',
            'Who is competition host?',
            'How many participants are in the competition?',
            'Who is on place 1 in the leaderboard?',
            'What techniques are useful for competition solution based on discussions?',
            'Summarize advices from discussion forum.',
        ]
        options_index = None
        if audio_question:
            questions_options = [audio_question] + questions_options
            options_index = 0
        user_question = st_free_text_select(
            label='Enter your question (type / choose from dropdown / record audio):',
            options=questions_options,
            index=options_index,
            placeholder='Type of select question',
            disabled=False,
            delay=300,
            label_visibility="visible",
        )
        if user_question == '':
            user_question = questions_options[0]

    # Ask button + output
    if st.button("Ask", use_container_width=True):
        logger.info(f"User asked: '{user_question}'")
        with st.spinner('Processing...'):
            logger.info(f"Getting answer from assistant using {search_type} retrieval")
            start_time = time.time()
            competition_slug = COMPETITION_2_SLUG[competition]
            assistant = assistants[competition_slug]
            search_type = SEARCH_TYPES_DICT[search_type]
            answer_data = ask_assistant(user_question, assistant, search_type, retrieval_n_results)
            end_time = time.time()
            logger.info(f"Answer received in {end_time - start_time:.2f} seconds")
            # st.success("Completed!")
            # st.write(answer_data['answer'])

            # voice the answer
            tmp_audio_file_path = './tmp_result.wav'
            text_to_speech(answer_data['answer'], tmp_audio_file_path)
            # play_audio(tmp_audio_file_path)

            # play answer audio
            #   apply custom CSS to hide the audio element - isn't working consistently
            st.markdown("""
                        <style>
                            .element-container:has(audio) {
                                position: absolute;
                                width: 1px;
                                height: 1px;
                                overflow: hidden;
                                opacity: 0.01;
                            }
                        </style>
                        """, unsafe_allow_html=True)
            st.audio(tmp_audio_file_path, format='audio/wav', autoplay=True)
            os.remove(tmp_audio_file_path)

            # print final text answer
            st.success("Completed!")
            st.write(answer_data['answer'])

            # Display monitoring information
            st.markdown('---')
            st.markdown('### Monitoring statistics')
            st.markdown(f"- Response time: {answer_data['response_time']:.2f} seconds")
            st.markdown(f"- Assistant model: `{answer_data['assistant_model']}`")
            st.markdown(f"- Relevance: {answer_data['relevance']}")
            st.markdown(f"- Relevance explanation: {answer_data['relevance_explanation']}")
            st.markdown(f"- Relevance model: `{answer_data['relevance_model']}`")
            st.markdown(f"- Total tokens: {answer_data['total_tokens']}")
            st.markdown(f"- LLM cost: ${answer_data['llm_cost']:.4f}")

            # Save conversation to database
            logger.info("Saving conversation to database...")
            # Generate a new question_id for each question
            st.session_state.current_question_id = str(uuid.uuid4())
            save_conversation(st.session_state.current_question_id, user_question, answer_data, COMPETITION_2_SLUG[competition])
            logger.info("Conversation saved successfully")


    # Feedback section
    st.markdown('### Feedback on answer quality')

    # Feedback buttons
    col1, col2 = st.columns(2)
    with col1:
        with stylable_container(
                "green",
                css_styles="""
            button {
                background-color: #00FF00;
                color: black;
            }""",
        ):
            if st.button("👍", use_container_width=True, type='secondary'):
                if st.session_state.current_question_id == -1:
                    logger.info('Dummy feedback received. Not saving to db')
                else:
                    st.session_state.count += 1
                    logger.info(f"Positive feedback received. New count: {st.session_state.count}")
                    save_feedback(st.session_state.current_question_id, 1)
                    logger.info("Positive feedback saved to database")
    with col2:
        if st.button("👎", use_container_width=True, type="primary"):
            if st.session_state.current_question_id == -1:
                logger.info('Dummy feedback received. Not saving to db')
            else:
                st.session_state.count += 1
                logger.info(f"Negative feedback received. New count: {st.session_state.count}")
                save_feedback(st.session_state.current_question_id, -1)
                logger.info("Negative feedback saved to database")

    st.write(f"Current feedbacks count: {st.session_state.count}")

    # Display recent conversations
    st.write('---')
    st.markdown("#### Recent Conversations")
    relevance_filter = st.selectbox("Filter by relevance:", ["All", "RELEVANT", "PARTIALLY_RELEVANT", "NON_RELEVANT"])
    recent_conversations = get_recent_conversations(limit=5,
                                                    relevance=relevance_filter if relevance_filter != "All" else None)
    with st.expander("See more items", expanded=True):
        for i,conv in enumerate(recent_conversations):
            st.write(f"Q: {conv['question']}")
            st.write(f"A: {conv['answer']}")
            st.write(f"Relevance: {conv['relevance']}")
            if i != len(recent_conversations) - 1:
                st.write("---")

    # Display feedback stats
    feedback_stats = get_feedback_stats()
    st.write('---')
    st.markdown("### Feedback Statistics")
    st.write(f"Thumbs up: {feedback_stats['thumbs_up'] or 0}")
    st.write(f"Thumbs down: {feedback_stats['thumbs_down'] or 0}")


logger.info("Kaggle Assistant application started")
assistants = init_assistants()
stt_model, tts_model = load_audio_models()
create_ui()
logger.info("Streamlit app loop completed")
