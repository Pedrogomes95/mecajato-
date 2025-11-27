// Global CSRF token - usar cookie do Django que é sempre criado
var csrf_token = null;

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function ensureCsrfToken(){
    if (csrf_token) return true;
    // try input element
    var token_element = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token_element && token_element.value){
        csrf_token = token_element.value;
        try{ document.cookie = 'csrftoken=' + encodeURIComponent(csrf_token) + '; path=/'; }catch(e){}
        console.log('ensureCsrfToken: obtained from input element');
        return true;
    }
    // try cookie
    csrf_token = getCookie('csrftoken');
    if (csrf_token){
        console.log('ensureCsrfToken: obtained from cookie');
        return true;
    }
    return false;
}

function init_csrf_token() {
    // Debug: mostrar cookies brutos para ajudar diagnóstico
    try {
        console.log('document.cookie:', document.cookie);
    } catch (e) {
        console.warn('Could not read document.cookie', e);
    }

    // A maneira MAIS CONFIÁVEL é usar o cookie 'csrftoken' que o Django SEMPRE cria
    // e valida nas requisições POST, independente de estar em um form ou não.
    csrf_token = getCookie('csrftoken');

    if (!csrf_token) {
        // Fallback: tenta pegar do input hidden (para casos onde o cookie não funciona)
        var token_element = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token_element) {
            csrf_token = token_element.value;
            console.log('CSRF token obtained from input element');
        }
    } else {
        console.log('CSRF token obtained from cookie');
    }

    if (csrf_token) {
        console.log('CSRF token initialized (trim):', csrf_token.substring(0, 20) + '...');
    } else {
        console.warn('⚠️  CSRF token not found - POST requests may fail with 403');
    }
}

function add_carro(){
    container = document.getElementById('form-carro')

    html = "<br>  <div class='row'> <div class='col-md'> <input type='text' placeholder='carro' class='form-control' name='carro' > </div> <div class='col-md'><input type='text' placeholder='Placa' class='form-control' name='placa' ></div> <div class='col-md'> <input type='number' placeholder='ano' class='form-control' name='ano'> </div> </div>"

    container.innerHTML += html
}

// Quando o documento estiver pronto, ligamos handlers para o modal do carro
document.addEventListener('DOMContentLoaded', function(){
    init_csrf_token();
    try{
        var carModal = document.getElementById('carModal');
        if (carModal){
            // antes de abrir, remover backdrops antigos para evitar sobreposição
            $(carModal).on('show.bs.modal', function(){
                var old = document.querySelectorAll('.modal-backdrop');
                old.forEach(function(el){ el.parentNode && el.parentNode.removeChild(el); });
            });
            // quando abrir, focar o primeiro campo e garantir que apenas 1 backdrop exista
            $(carModal).on('shown.bs.modal', function(){
                var b = document.querySelectorAll('.modal-backdrop');
                if (b.length > 1) {
                    for (var i = 0; i < b.length - 1; i++) { if (b[i].parentNode) b[i].parentNode.removeChild(b[i]); }
                }
                // garantir z-index alto para o modal
                this.style.zIndex = 2001;
                var t = document.getElementById('car-title');
                if (t) t.focus();
            });
            // quando fechar, remover backdrops remanescentes que possam bloquear interação
            $(carModal).on('hidden.bs.modal', function(){
                var b = document.querySelectorAll('.modal-backdrop');
                b.forEach(function(el){ el.parentNode && el.parentNode.removeChild(el); });
            });
        }

        // Handler global para quaisquer modais: garantir cleanup e foco no primeiro campo
        $(document).on('shown.bs.modal', '.modal', function(){
            var b = document.querySelectorAll('.modal-backdrop');
            if (b.length > 1) {
                for (var i = 0; i < b.length - 1; i++) { if (b[i].parentNode) b[i].parentNode.removeChild(b[i]); }
            }
            this.style.zIndex = 2001;
            var first = this.querySelector('input, textarea, select, button');
            if (first) first.focus();
        });
    }catch(e){
        console.warn('Modal handlers init error', e);
    }
    
    // Garantir que o token CSRF seja inicializado DEPOIS que todos os elementos estejam prontos
    setTimeout(function() {
        init_csrf_token();
    }, 100);
});

function exibir_form(tipo){

    add_cliente = document.getElementById('adicionar-cliente')
    att_cliente = document.getElementById('att_cliente')

    if(tipo == "1"){
        att_cliente.style.display = "none"
        add_cliente.style.display = "block"

    }else if(tipo == "2"){
        add_cliente.style.display = "none";
        att_cliente.style.display = "block"
    }

}


function dados_cliente(){
    cliente = document.getElementById('cliente-select')
    id_cliente = cliente.value

    if (!id_cliente) {
        alert('Por favor, selecione um cliente');
        return;
    }

    // if (!ensureCsrfToken()) {
    //     alert('Erro: Token CSRF não encontrado. Recarregue a página.');
    //     console.error('CSRF token is null or empty', { csrf_token });
    //     return;
    // }

    data = new FormData()
    data.append('id_cliente', id_cliente)
    data.append('csrfmiddlewaretoken', csrf_token)

    fetch("/clientes/atualiza_cliente/",{
        method: "POST",
        body: data

    }).then(function(result){
        if (!result.ok) {
            throw new Error('HTTP error status: ' + result.status);
        }
        return result.json()
    }).then(function(data){
        var form_att = document.getElementById('form-att-cliente');
        if (form_att) {
            form_att.style.display = 'block';
        }
        
        id = document.getElementById('id')
        id.value = data['cliente_id']

        nome = document.getElementById('nome')
        nome.value = data['cliente']['nome']

        sobrenome = document.getElementById('sobrenome')
        sobrenome.value = data['cliente']['sobrenome']

        cpf = document.getElementById('cpf')
        cpf.value = data['cliente']['cpf']

        email = document.getElementById('email')
        email.value = data['cliente']['email']

        div_carros = document.getElementById('carros')

        for(i=0; i<data['carros'].length; i++){
            div_carros.innerHTML += "\<form action='/clientes/update_carro/" + data['carros'][i]['id'] +"' method='POST'>\
                <div class='row'>\
                        <div class='col-md'>\
                            <input class='form-control' name='carro' type='text' value='" + data['carros'][i]['fields']['carro'] + "'>\
                        </div>\
                        <div class='col-md'>\
                            <input class='form-control' name='placa' type='text' value='" + data['carros'][i]['fields']['placa'] + "'>\
                        </div>\
                        <div class='col-md'>\
                            <input class='form-control' type='text' name='ano' value='" + data['carros'][i]['fields']['ano'] + "' >\
                        </div>\
                        <div class='col-md'>\
                            <input class='btn btn-lg btn-success' type='submit'>\
                        </div>\
                    </form>\
                    <div class='col-md'>\
                        <a href='/clientes/excluir_carro/"+ data['carros'][i]['id'] +"' class='btn btn-lg btn-danger'>EXCLUIR</a>\
                    </div>\
                </div><br>"
        }
    }).catch(function(error){
        console.error('Erro ao carregar dados do cliente:', error);
        alert('Erro ao carregar dados do cliente: ' + error);
    })


}


function update_cliente(){
    nome = document.getElementById('nome').value
    sobrenome = document.getElementById('sobrenome').value
    email = document.getElementById('email').value
    cpf = document.getElementById('cpf').value
    id = document.getElementById('id').value

    if (!id) {
        alert('Erro: ID do cliente não encontrado. Por favor, selecione um cliente primeiro.');
        console.error('update_cliente: id is empty or null', { id });
        return;
    }

    if (!ensureCsrfToken()){
        alert('Erro: Token CSRF não encontrado. Recarregue a página.');
        console.error('update_cliente: csrf token missing');
        return;
    }

    fetch('/clientes/update_cliente/' + id, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            nome: nome,
            sobrenome: sobrenome,
            email: email,
            cpf: cpf,
        })

    }).then(function(result){
        return result.json()
    }).then(function(data){

        if(data['status'] == '200'){
            nome = data['nome']
            sobrenome = data['sobrenome']
            email = data['email']
            cpf = data['cpf']
            console.log('Dados alterado com sucesso')
        }else{
            console.log('Ocorreu algum erro')
        }

    })

}
