import os
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sua-chave-secreta-aqui'  # Mude para algo seguro e único
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Classe simples para usuário admin
class AdminUser(UserMixin):
    def __init__(self, username):
        self.id = username

# Credenciais de admin (ALTERE AQUI: edite esses valores diretamente no código)
ADMIN_USERNAME = 'admin'  # Altere para o usuário desejado
ADMIN_PASSWORD = 'sua-senha-aqui'  # Altere para a senha desejada (será hasheada automaticamente)

# Hash da senha (feito automaticamente)
admin_pass_hash = generate_password_hash(ADMIN_PASSWORD)

@login_manager.user_loader
def load_user(user_id):
    if user_id == ADMIN_USERNAME:
        return AdminUser(user_id)
    return None

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'Erro: Nenhum arquivo enviado', 400
    file = request.files['file']
    if file.filename == '':
        return 'Erro: Nenhum arquivo selecionado', 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# Rotas admin
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and check_password_hash(admin_pass_hash, password):
            user = AdminUser(username)
            login_user(user)
            return redirect(url_for('admin_files'))
        flash('Credenciais inválidas')
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Login Admin - RAZIEL SERVER 🦇</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                body { background: linear-gradient(135deg, #0d0d0d 0%, #2d1b3d 50%, #4a0e4e 100%); color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
                .glass-container { backdrop-filter: blur(20px); background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37); padding: 2rem; max-width: 400px; width: 100%; }
                .form-control { background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 15px; color: #f5f5f5; padding: 1rem; }
                .form-control:focus { background: rgba(255, 255, 255, 0.2); border-color: #9c27b0; box-shadow: 0 0 10px rgba(156, 39, 176, 0.5); color: #ffffff; }
                .btn-primary { background: linear-gradient(45deg, #9c27b0, #e91e63); border: none; border-radius: 25px; padding: 0.75rem 2rem; font-weight: bold; }
                .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(156, 39, 176, 0.5); }
                .alert { background: rgba(255, 0, 0, 0.1); border: 1px solid rgba(255, 0, 0, 0.2); color: #ffcccc; }
            </style>
        </head>
        <body>
            <div class="glass-container">
                <h1 class="text-center" style="background: linear-gradient(45deg, #9c27b0, #e91e63); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Login Admin 🦇</h1>
                <form method="POST">
                    <div class="mb-3">
                        <label for="username" class="form-label"><i class="fas fa-user"></i> Usuário:</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label"><i class="fas fa-lock"></i> Senha:</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100"><i class="fas fa-sign-in-alt"></i> Entrar</button>
                </form>
                {% with messages = get_flashed_messages() %}
                    {% if messages %}
                        <div class="alert mt-3">
                            {% for message in messages %}
                                <p>{{ message }}</p>
                            {% endfor %}
                        </div>
                    {% endif %}
                {% endwith %}
                <p class="text-center mt-3"><a href="/" style="color: #9c27b0;">Voltar ao Início</a></p>
            </div>
        </body>
        </html>
    ''')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/files')
@login_required
def admin_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    file_list = '''
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Gerenciar Arquivos - RAZIEL SERVER 🦇</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                body { background: linear-gradient(135deg, #0d0d0d 0%, #2d1b3d 50%, #4a0e4e 100%); color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; min-height: 100vh; margin: 0; }
                .glass-container { backdrop-filter: blur(20px); background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37); padding: 2rem; margin: 2rem auto; max-width: 800px; }
                .list-group-item { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; margin-bottom: 0.5rem; color: #ffffff; }
                .list-group-item:hover { background: rgba(255, 255, 255, 0.1); }
                .btn-danger { background: linear-gradient(45deg, #e91e63, #f44336); border: none; border-radius: 20px; padding: 0.5rem 1rem; font-size: 0.9rem; }
                .btn-danger:hover { transform: translateY(-1px); box-shadow: 0 4px 15px rgba(233, 30, 99, 0.5); }
                .btn-secondary { background: linear-gradient(45deg, #4a0e4e, #3a0144); border: none; border-radius: 20px; padding: 0.5rem 1rem; }
            </style>
        </head>
        <body>
            <div class="glass-container">
                <h1 style="background: linear-gradient(45deg, #9c27b0, #e91e63); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Gerenciar Arquivos (Admin) 🦇</h1>
                <p class="text-muted">Aqui você pode apagar arquivos do servidor.</p>
                {% if files %}
                    <ul class="list-group">
                        {% for file in files %}
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <span><i class="fas fa-file"></i> {{ file }}</span>
                                <a href="/admin/delete/{{ file }}" class="btn btn-danger btn-sm" onclick="return confirm('Tem certeza que deseja apagar este arquivo?')"><i class="fas fa-trash"></i> Apagar</a>
                            </li>
                        {% endfor %}
                    </ul>
                {% else %}
                    <p class="text-muted"><i class="fas fa-folder-open"></i> Nenhum arquivo disponível para apagar.</p>
                {% endif %}
                <div class="mt-3">
                    <a href="/admin/logout" class="btn btn-secondary"><i class="fas fa-sign-out-alt"></i> Sair</a>
                    <a href="/" class="btn btn-secondary ms-2"><i class="fas fa-home"></i> Voltar ao Início</a>
                </div>
            </div>
        </body>
        </html>
    '''
    return render_template_string(file_list, files=files)

@app.route('/admin/delete/<filename>')
@login_required
def admin_delete(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('Arquivo apagado com sucesso')
    else:
        flash('Arquivo não encontrado')
    return redirect(url_for('admin_files'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
