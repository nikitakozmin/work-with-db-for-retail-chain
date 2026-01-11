from flask import Flask, request, jsonify
from db import SessionLocal
from queries import *
import inspect

def create_app():
    app = Flask(__name__)

    @app.route("/") 
    def index():
        return "Flask работает"
    
    
    def call_func(func):
        def query_func():
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            args = dict()
            for arg in params[1:]:
                v = request.args.get(arg, None)
                if v != None:
                    args[arg] = v
            args["session"]=SessionLocal()
            return str(func(**args))
        
        return query_func 
        
    for func in queries: # queries - список внутри модуля queries
        app.add_url_rule(f"/{func.__name__}", endpoint=func.__name__, view_func=call_func(func))
    
    
    @app.route("/hack_me")
    def hack_me():
        session = SessionLocal()
        try:
            value = request.args.get("value", "")
            return str(bad_query_like(session, value))
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            session.rollback()
        finally:
            session.close()
            
    @app.route("/bad_query")        
    def bad_query_():
        session = SessionLocal()
        try:
            value = request.args.get("value", "")
            return str(bad_query_id(session, value))
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            session.rollback()
        finally:
            session.close()
        
    
    @app.route("/request")
    def execute_queries_():
        session = SessionLocal()
        try:
            return jsonify(execute_queries(session))
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            session.rollback()
        finally:
            session.close()

    

    return app
