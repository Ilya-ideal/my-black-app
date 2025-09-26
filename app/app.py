from flask import Flask, render_template_string

app = Flask(__name__)

# HTML шаблон с черным фоном
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Мое Приложение</title>
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
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Мое Приложение с Черным Фоном!</h1>
        <p>Версия: {{ version }}</p>
        <p>Фон был успешно изменен.</p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    # Можно использовать версию из переменных окружения
    import os
    version = os.getenv('APP_VERSION', '1.0.0')
    return render_template_string(HTML_TEMPLATE, version=version)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)