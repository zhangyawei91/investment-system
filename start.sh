#!/bin/bash
cd "$(dirname "$0")"
echo "启动威少投资智脑系统..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
