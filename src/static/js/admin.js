// Definir Constantes
const email = document.getElementById("email");
const password = document.getElementById("password");
const form = document.getElementById("form");
const parrafo = document.getElementById("warnings")

//Cuando se envie el formulario o se presione el botón 
form.addEventListener("submit",e=>{
    //Prevenir lo del default
    e.preventDefault();
    let regexEmail = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/
    let warnings="";
    let entrar= false
    if (email.value.length == 0){
        warnings += 'El campo de Correo electrónico no puede estar vacio <br>';
        entrar= true
    }
    if (email.value.length > 70){
        warnings +='El correo electrónico no debe tener más de 70 caracteres <br>';
        entrar= true
    }
    // Validar el email
    console.log(regexEmail.test(email.value))
    if (!regexEmail.test(email.value)){
        warnings +='El correo electrónico no es válido <br>';
        entrar=true
    }
    if (password.value.length == 0){
        warnings +='La contraseña no puede estar vacia <br>';
        entrar=true
    }
    if (email.value !== 'rodolfarias@gmail.com'){
        warnings +='El correo electrónico no es válido <br>';
        entrar= true
    }
    if (password.value !== 'rodolfo528'){
        warnings +='La contraseña no es válida <br>';
        entrar=true
    }
    if(entrar){
        parrafo.innerHTML = warnings
    } else{
        parrafo.innerHTML = ""
        alert('Bienvenido Administrador')
    }
})