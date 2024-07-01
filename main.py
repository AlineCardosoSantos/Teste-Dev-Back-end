from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import sqlite3
from collections import defaultdict
from typing import List, Dict, Any
import requests
import json

app = FastAPI()

# Problema 01
# Criar uma API para disponibilizar os dados para a 
# composição de um dashboard de chamados de suporte

class Ticket(BaseModel):
    Código: str
    Título: str
    Cliente: str
    Data_Abertura: str
    Data_Encerramento: str
    Módulo: str

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.post("/tickets")
def create_ticket(ticket: Ticket):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO ticket (TITLE, FK_ID_CLIENT, OPENING_DATE, CLOSING_DATE, FK_ID_MODULE)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        ticket.Título,
        ticket.Código,
        ticket.Data_Abertura,
        ticket.Data_Encerramento,
        ticket.Módulo
    ))
    conn.commit()
    conn.close()

    return ticket

@app.get('/tickets')
def get_tickets(mes: int, ano: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""SELECT t.*, c.nome as Cliente, m.nome as Modulo FROM ticket t 
                JOIN modulo m on t.FK_ID_MODULE = m.ID
                JOIN cliente c on t.FK_ID_CLIENT = c.ID""")
    
    rows = cur.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="Tickets não encontrados para o mês e ano fornecidos")

    filtered_tickets = []
    for row in rows:
        filtered_tickets.append(dict(row))


    tickets_por_cliente = defaultdict(list)
    for ticket in filtered_tickets:
        tickets_por_cliente[ticket['Cliente']].append(ticket)

    dados_agrupados_por_cliente = []
    for cliente, tickets in tickets_por_cliente.items():
        dados_agrupados_por_cliente.append({"Cliente": cliente, "Tickets": tickets})
    

    tickets_por_modulo = defaultdict(list)
    for ticket in filtered_tickets:
        tickets_por_modulo[ticket['Modulo']].append(ticket)

    dados_agrupados_por_modulo = []
    for modulo, tickets in tickets_por_modulo.items():
        dados_agrupados_por_modulo.append({"Módulo": modulo, "Tickets": tickets})


    return [filtered_tickets, dados_agrupados_por_cliente, dados_agrupados_por_modulo]


# Problema 2 
# Criar uma API que receba um um prato e retorne a lista de receitas encontradas.
@app.get('/receitas')
def get_receitas(receita: str):
    req = requests.get(f'https://forkify-api.herokuapp.com/api/search?q={receita}')
    response = json.loads(req.content)

    return response


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
