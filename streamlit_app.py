    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% {
            /* Neón Rojo Encendido */
            text-shadow: 
                0 0 4px #ff0000,
                0 0 11px #ff0000,
                0 0 19px #ff0000,
                0 0 40px #ff4b4b,
                0 0 80px #ff4b4b,
                0 0 90px #ff4b4b,
                0 0 100px #ff4b4b,
                0 0 150px #ff4b4b;
            color: #ff4b4b;
        }
        20%, 24%, 55% {        
            /* Neón Rojo Apagado (Efecto roto) */
            text-shadow: none;
            color: #330000; 
        }
    }

    .ruth-header {
        text-align: center;
        padding-top: 2rem;
        letter-spacing: 1.5rem;
        font-weight: 100;
        color: #ff4b4b; /* Letra roja */
        font-size: 6rem;
        animation: flicker 3s infinite alternate;
        margin-bottom: 0px;
    }
