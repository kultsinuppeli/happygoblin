# happygoblin
Magic the Gathering game tracker / life counter

This is a Web2Py application. (http://www.web2py.com/). 

Current special dependecies
 * Mozilla persona for authentication

## Deploying

Copy this to your applications directory. Add a file modules/config.py with the following parameters

    dal_url = "sqlite://storage.sqlite"
    persona_audience = "http://127.0.0.1:8000"
    base_url = "/happygoblin/"
    websocket_server = "127.0.0.1:8888/"
    websocket_key ="testkey"

## Running

Run this as a web2py application. In addition this depends on websockets for communication. Check instructions to run this from your web2py installtion under

    gluon/contrib/websocket_messaging.py
