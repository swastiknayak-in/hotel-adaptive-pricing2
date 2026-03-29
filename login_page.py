import streamlit as st


def show_login_page():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600;700&family=Jost:wght@300;400;500&display=swap');

    .login-hero {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1209 50%, #0d0d0d 100%);
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .hotel-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 4rem;
        font-weight: 300;
        color: #D4AF37;
        letter-spacing: 0.15em;
        text-align: center;
        margin-bottom: 0.2rem;
        text-shadow: 0 0 40px rgba(212,175,55,0.3);
    }

    .hotel-subtitle {
        font-family: 'Jost', sans-serif;
        font-size: 0.85rem;
        font-weight: 300;
        color: #8a8a8a;
        letter-spacing: 0.4em;
        text-align: center;
        text-transform: uppercase;
        margin-bottom: 3rem;
    }

    .gold-divider {
        width: 80px;
        height: 1px;
        background: linear-gradient(90deg, transparent, #D4AF37, transparent);
        margin: 1.5rem auto;
    }

    .role-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(212,175,55,0.2);
        border-radius: 2px;
        padding: 2rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'Jost', sans-serif;
    }

    .role-card:hover {
        background: rgba(212,175,55,0.08);
        border-color: #D4AF37;
        transform: translateY(-2px);
    }

    .role-icon {
        font-size: 2.5rem;
        margin-bottom: 0.8rem;
    }

    .role-name {
        font-size: 1.1rem;
        font-weight: 500;
        color: #D4AF37;
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }

    .role-desc {
        font-size: 0.78rem;
        color: #666;
        letter-spacing: 0.05em;
        margin-top: 0.4rem;
    }

    .welcome-tag {
        font-family: 'Jost', sans-serif;
        font-size: 0.7rem;
        letter-spacing: 0.5em;
        color: #D4AF37;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 0.5rem;
        opacity: 0.7;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<div class="welcome-tag">Welcome to</div>', unsafe_allow_html=True)
    st.markdown('<div class="hotel-title">GRANDEUR</div>', unsafe_allow_html=True)
    st.markdown('<div class="hotel-subtitle">Adaptive Pricing & Revenue Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown(
        "<p style='text-align:center;font-family:Jost,sans-serif;color:#666;font-size:0.9rem;"
        "letter-spacing:0.08em;'>Select your access role to continue</p>",
        unsafe_allow_html=True
    )
    st.markdown("")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name = st.text_input(
            "Your Name",
            placeholder="Enter your name",
            key="login_name",
            label_visibility="collapsed",
        )
        st.markdown(
            "<p style='font-family:Jost,sans-serif;font-size:0.75rem;color:#555;"
            "letter-spacing:0.1em;text-align:center;margin-bottom:1rem;'>YOUR NAME</p>",
            unsafe_allow_html=True
        )

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
            <div class="role-card">
                <div class="role-icon">🛎️</div>
                <div class="role-name">Guest</div>
                <div class="role-desc">Browse & book rooms</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Enter as Guest", use_container_width=True, key="btn_customer"):
                if name.strip():
                    st.session_state["role"] = "Customer"
                    st.session_state["username"] = name.strip()
                    st.rerun()
                else:
                    st.warning("Please enter your name.")

        with col_b:
            st.markdown("""
            <div class="role-card">
                <div class="role-icon">📊</div>
                <div class="role-name">Manager</div>
                <div class="role-desc">Analytics & pricing</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Enter as Manager", use_container_width=True, key="btn_manager"):
                if name.strip():
                    st.session_state["role"] = "Manager"
                    st.session_state["username"] = name.strip()
                    st.rerun()
                else:
                    st.warning("Please enter your name.")

    st.markdown("")
    st.markdown(
        "<p style='text-align:center;font-family:Jost,sans-serif;color:#333;"
        "font-size:0.7rem;letter-spacing:0.15em;'>POWERED BY ADAPTIVE ML PRICING ENGINE</p>",
        unsafe_allow_html=True
    )
