from flask import Response
from app import app

@app.route('/robot-test')
def robot_test():
    """Simple page to test fresh robot display without cache"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Robot Test - Fresh Load</title>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <style>
        body {
            background: linear-gradient(135deg, #0f0f23, #1a1a2e);
            color: white;
            font-family: Arial, sans-serif;
            padding: 20px;
            min-height: 100vh;
            margin: 0;
        }
        
        .test-container {
            text-align: center;
            padding: 40px;
        }
        
        .timestamp {
            color: #06b6d4;
            font-weight: bold;
            margin-bottom: 30px;
        }
        
        /* Fresh Robot Mascot */
        .ai-robot-mascot {
            position: relative;
            display: inline-block;
            width: 80px;
            height: 80px;
            margin: 20px auto;
            animation: robotFloat 3s ease-in-out infinite;
        }
        
        .robot-head {
            width: 40px;
            height: 32px;
            background: linear-gradient(135deg, #8b5cf6, #06b6d4);
            border-radius: 16px;
            position: absolute;
            top: 0;
            left: 20px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 3px 12px rgba(139, 92, 246, 0.4);
        }
        
        .robot-body {
            width: 48px;
            height: 36px;
            background: linear-gradient(135deg, #8b5cf6, #06b6d4);
            border-radius: 12px;
            position: absolute;
            top: 28px;
            left: 16px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 3px 12px rgba(139, 92, 246, 0.4);
        }
        
        .robot-eyes {
            position: absolute;
            top: 12px;
            left: 28px;
            display: flex;
            gap: 8px;
        }
        
        .robot-eye {
            width: 6px;
            height: 6px;
            background: white;
            border-radius: 50%;
            animation: robotBlink 4s infinite;
        }
        
        .robot-mouth {
            position: absolute;
            top: 22px;
            left: 32px;
            width: 12px;
            height: 3px;
            background: white;
            border-radius: 2px;
        }
        
        .robot-antenna {
            position: absolute;
            top: -6px;
            left: 38px;
            width: 2px;
            height: 12px;
            background: white;
        }
        
        .robot-antenna::after {
            content: '';
            position: absolute;
            top: -3px;
            left: -2px;
            width: 6px;
            height: 6px;
            background: #06b6d4;
            border-radius: 50%;
        }
        
        .robot-arm {
            width: 6px;
            height: 20px;
            background: linear-gradient(135deg, #8b5cf6, #06b6d4);
            border-radius: 3px;
            position: absolute;
            top: 35px;
        }
        
        .robot-arm.left {
            left: 8px;
            animation: robotWaveLeft 4s ease-in-out infinite;
        }
        
        .robot-arm.right {
            right: 8px;
            animation: robotWaveRight 4s ease-in-out infinite;
        }
        
        .robot-legs {
            position: absolute;
            bottom: 6px;
            left: 30px;
            display: flex;
            gap: 6px;
        }
        
        .robot-leg {
            width: 6px;
            height: 12px;
            background: linear-gradient(135deg, #8b5cf6, #06b6d4);
            border-radius: 3px;
        }
        
        .robot-thought {
            position: absolute;
            top: -25px;
            right: -5px;
            background: rgba(255, 255, 255, 0.9);
            color: #1a1a1a;
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: 600;
            opacity: 0;
            animation: robotThought 6s ease-in-out infinite;
            white-space: nowrap;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .robot-thought::after {
            content: '';
            position: absolute;
            bottom: -3px;
            left: 8px;
            width: 0;
            height: 0;
            border-left: 3px solid transparent;
            border-right: 3px solid transparent;
            border-top: 3px solid rgba(255, 255, 255, 0.9);
        }
        
        @keyframes robotFloat {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
        }
        
        @keyframes robotBlink {
            0%, 90%, 100% { opacity: 1; }
            95% { opacity: 0; }
        }
        
        @keyframes robotWaveLeft {
            0%, 100% { transform: rotate(0deg); }
            25% { transform: rotate(-10deg); }
            75% { transform: rotate(5deg); }
        }
        
        @keyframes robotWaveRight {
            0%, 100% { transform: rotate(0deg); }
            25% { transform: rotate(10deg); }
            75% { transform: rotate(-5deg); }
        }
        
        @keyframes robotThought {
            0%, 70%, 100% { opacity: 0; }
            10%, 60% { opacity: 1; }
        }
        
        .back-link {
            color: #06b6d4;
            text-decoration: none;
            margin-top: 30px;
            display: inline-block;
            padding: 10px 20px;
            border: 1px solid #06b6d4;
            border-radius: 5px;
        }
        
        .back-link:hover {
            background: #06b6d4;
            color: white;
        }
    </style>
</head>
<body>
    <div class="test-container">
        <h1>Fresh Robot Test</h1>
        <div class="timestamp">Fresh Load: """ + str(__import__('time').time()) + """</div>
        
        <div class="ai-robot-mascot">
            <div class="robot-thought">Fresh robot design!</div>
            <div class="robot-head">
                <div class="robot-eyes">
                    <div class="robot-eye"></div>
                    <div class="robot-eye"></div>
                </div>
                <div class="robot-mouth"></div>
                <div class="robot-antenna"></div>
            </div>
            <div class="robot-body"></div>
            <div class="robot-arm left"></div>
            <div class="robot-arm right"></div>
            <div class="robot-legs">
                <div class="robot-leg"></div>
                <div class="robot-leg"></div>
            </div>
        </div>
        
        <p>This is the fresh robot design without any cache. You should see:</p>
        <ul style="text-align: left; max-width: 400px; margin: 20px auto;">
            <li>Purple-blue gradient head and body</li>
            <li>Two white blinking eyes</li>
            <li>White antenna with blue tip</li>
            <li>Waving arms on both sides</li>
            <li>Two legs at the bottom</li>
            <li>Floating animation</li>
        </ul>
        
        <a href="/" class="back-link">← Back to Main Interface</a>
    </div>
</body>
</html>
    """
    
    response = Response(html)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response