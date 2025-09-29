from flask import Flask, render_template_string, jsonify, request
import os
import logging
import time
from datetime import datetime
import psutil
import platform

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# HTML шаблон с черным фоном
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Мое Приложение с Черным Фоном</title>
    <style>
        body {
            background-color: black;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            padding: 20px;
            border: 2px solid #fff;
            border-radius: 10px;
            background-color: #111;
        }
        h1 {
            color: #4CAF50;
        }
        .status {
            color: #4CAF50;
            font-weight: bold;
        }
        .metrics {
            margin-top: 20px;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Мое CI/CD Приложение</h1>
        <p class="status">Фон успешно изменен на черный!</p>
        <p>Версия: <strong>{{ version }}</strong></p>
        <p>Время развертывания: {{ deploy_time }}</p>
        <p>Хост: {{ hostname }}</p>
        
        <div class="metrics">
            <h3>📊 Метрики системы:</h3>
            <p>💾 Память: {{ memory_usage }}%</p>
            <p>🖥️ CPU: {{ cpu_usage }}%</p>
            <p>📁 Диск: {{ disk_usage }}%</p>
            <p>🕒 Время работы: {{ uptime }}</p>
        </div>
        
        <div style="margin-top: 20px;">
            <a href="/health" style="color: #4CAF50; margin-right: 15px;">Health Check</a>
            <a href="/metrics" style="color: #4CAF50; margin-right: 15px;">Metrics</a>
            <a href="/logs" style="color: #4CAF50;">Logs</a>
        </div>
    </div>
</body>
</html>
"""

def get_system_metrics():
    """Получение метрик системы"""
    memory = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=1)
    disk = psutil.disk_usage('/')
    
    return {
        'memory_usage': round(memory.percent, 2),
        'cpu_usage': cpu,
        'disk_usage': round(disk.percent, 2),
        'uptime': str(datetime.now() - start_time).split('.')[0]
    }

start_time = datetime.now()

@app.route('/')
def home():
    logger.info("Главная страница запрошена")
    
    version = os.getenv('APP_VERSION', '1.0.0')
    deploy_time = os.getenv('DEPLOY_TIME', 'Неизвестно')
    hostname = os.getenv('HOSTNAME', platform.node())
    
    metrics = get_system_metrics()
    
    return render_template_string(HTML_TEMPLATE, 
                                version=version, 
                                deploy_time=deploy_time,
                                hostname=hostname,
                                **metrics)

@app.route('/health')
def health():
    """Health check endpoint"""
    logger.info("Health check запрошен")
    
    try:
        metrics = get_system_metrics()
        
        # Проверяем критичные метрики
        status = 'healthy'
        if metrics['memory_usage'] > 90:
            status = 'degraded'
            logger.warning(f"Высокое использование памяти: {metrics['memory_usage']}%")
        if metrics['cpu_usage'] > 85:
            status = 'degraded'
            logger.warning(f"Высокое использование CPU: {metrics['cpu_usage']}%")
        
        return jsonify({
            'status': status,
            'service': 'black-background-app',
            'timestamp': datetime.now().isoformat(),
            'version': os.getenv('APP_VERSION', '1.0.0'),
            'metrics': metrics
        })
    
    except Exception as e:
        logger.error(f"Ошибка health check: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/metrics')
def metrics():
    """Metrics endpoint для Prometheus"""
    logger.info("Метрики запрошены")
    
    try:
        metrics_data = get_system_metrics()
        
        # Формат Prometheus
        prometheus_metrics = f"""# HELP app_memory_usage Memory usage percentage
# TYPE app_memory_usage gauge
app_memory_usage {metrics_data['memory_usage']}

# HELP app_cpu_usage CPU usage percentage
# TYPE app_cpu_usage gauge
app_cpu_usage {metrics_data['cpu_usage']}

# HELP app_disk_usage Disk usage percentage
# TYPE app_disk_usage gauge
app_disk_usage {metrics_data['disk_usage']}

# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds counter
app_uptime_seconds {int((datetime.now() - start_time).total_seconds())}

# HELP app_http_requests_total Total HTTP requests
# TYPE app_http_requests_total counter
app_http_requests_total {request_count}
"""
        
        return prometheus_metrics, 200, {'Content-Type': 'text/plain'}
    
    except Exception as e:
        logger.error(f"Ошибка получения метрик: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/logs')
def show_logs():
    """Endpoint для просмотра логов"""
    logger.info("Логи запрошены")
    
    # В реальном приложении здесь можно читать из файла логов
    log_entries = [
        f"{datetime.now()} - INFO - Приложение запущено",
        f"{datetime.now()} - INFO - Health check выполнен",
        f"{datetime.now()} - INFO - Метрики собраны"
    ]
    
    return jsonify({
        'logs': log_entries,
        'count': len(log_entries)
    })

# Счетчик запросов для метрик
request_count = 0

@app.before_request
def count_requests():
    global request_count
    request_count += 1
    logger.info(f"Запрос: {request.method} {request.path}")

if __name__ == '__main__':
    logger.info("Запуск приложения...")
    app.run(host='0.0.0.0', port=5000, debug=False)