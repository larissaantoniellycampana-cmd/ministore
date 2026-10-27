
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_connection
import mysql.connector

produtos_bp = Blueprint('produtos', __name__, template_folder='templates')


@produtos_bp.route('/produtos')
def listar():
    conn = None
    cursor = None
    produtos = []

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM produtos ORDER BY nome')
        produtos = cursor.fetchall()

    except mysql.connector.Error as e:
        flash(f'Erro ao buscar produtos: {e}', 'danger')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('lista_produto.html', produto=produtos)


@produtos_bp.route('/produtos/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        nome = request.form['nome']
        categoria = request.form.get('categoria', '')
        preco = request.form.get('preco') or 0
        estoque = request.form.get('estoque') or 0
        descricao = request.form.get('descricao', '')

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            sql = '''INSERT INTO produtos
                     (nome, categoria, preco, estoque, descricao)
                     VALUES (%s, %s, %s, %s, %s)'''

            cursor.execute(sql, (nome, categoria, preco, estoque, descricao))
            conn.commit()

            flash('Produto cadastrado com sucesso!', 'success')
            return redirect(url_for('produtos.listar'))

        except mysql.connector.Error as e:
            flash(f'Erro ao cadastrar produto: {e}', 'danger')

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('form_produto.html', produto=None)


@produtos_bp.route('/produtos/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            nome = request.form['nome']
            categoria = request.form.get('categoria', '')
            preco = request.form.get('preco') or 0
            estoque = request.form.get('estoque') or 0
            descricao = request.form.get('descricao', '')

            sql = '''UPDATE produtos
                     SET nome=%s, categoria=%s, preco=%s,
                         estoque=%s, descricao=%s
                     WHERE id=%s'''

            cursor.execute(sql, (nome, categoria, preco, estoque, descricao, id))
            conn.commit()

            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('produtos.listar'))

        # Se não for POST é GET — busca o registro para o formulário
        cursor.execute('SELECT * FROM produtos WHERE id = %s', (id,))
        produto = cursor.fetchone()

        if not produto:
            flash('Produto não encontrado.', 'danger')
            return redirect(url_for('produtos.listar'))

    except mysql.connector.Error as e:
        flash(f'Erro: {e}', 'danger')
        return redirect(url_for('produtos.listar'))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('form_produto.html', produto=produto)


@produtos_bp.route('/produtos/<int:id>/excluir', methods=['POST'])
def excluir(id):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM produtos WHERE id = %s', (id,))
        conn.commit()

        flash('Produto excluído com sucesso!', 'success')

    except mysql.connector.Error as e:
        flash(f'Erro ao excluir produto: {e}', 'danger')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('produtos.listar'))
