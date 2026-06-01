
const socket = io()

socket.on(
    "atualizar", async () => {

        console.log("evento recebido")

        const resposta =
            await fetch("/dados-painel")
        
        const dados =
            await resposta.json()

        console.log(dados.chamados)
    }
)

function atualizarChamados(chamados){
    const lista = 
        document.getElementById("lista-chamados")

    lista.innerHTML = ""

    chamados.forEach(chamado => {
        lista.innerHTML += `
            <div class="linha">
                <div>${chamado.chamado}</div>
                <div>${chamado.status}</div>
                <div>${chamado.tecnico || "Nenhum  técnico"}</div>
            </div>
        `
    })
}

async function atualizarPainel(){
    try {
        const resposta =
            await fetch("/dados-painel")

        const dados =
            await resposta.json()

        console.log("DADOS: ", dados)

        atualizarCards(dados)

        atualizarChamados(
            dados.chamados
        )

        atualizarApoio(
            dados.apoio_status,
            dados.apoio_nome
        )

    } catch (error) {
        console.error("Erro ao atualizar painel:", error)
    }
}

function atualizarCards(dados) {

    const cardAtual = 
        document.getElementById(
            "card-atual"
        )
    
    const cardProximo =
        document.getElementById(
            "card-proximo"
        )

    if (cardAtual && dados.atual) {

        const h2 = 
            cardAtual.querySelector("h2")
        
        const p =
            cardAtual.querySelector("p")

        if (h2) {
            h2.innerText =
                dados.atual.analista || "-"
        }

        if (p) {
            p.innerText = 
                `${dados.atual.horario_inicio} até ${dados.atual.horario_fim}`
        }        
    }

    if (cardProximo && dados.proximo) {

        const h3 = 
            cardProximo.querySelector("h3")
        
        const p = 
            cardProximo.querySelector("p")
        
        if (h3) {
            h3.innerText =
                dados.proximo.analista || "-"
        }

        if (p) {
            p.innerText =
            `${dados.proximo.horario_inicio} até ${dados.proximo.horario_fim}`
        }
    }
}
// LOGIN ADMIN
const btnLoginAdmin =
    document.getElementById(
        "btn-login-admin"
    )

if (btnLoginAdmin) {

    btnLoginAdmin.addEventListener(
        "click",
        async () => {

            const senha =
                document.getElementById(
                    "senha-admin"
                ).value

            const formData =
                new FormData()

            formData.append(
                "senha",
                senha
            )

            const resposta =
                await fetch(
                    "/login-admin",
                    {
                        method: "POST",
                        body: formData
                    }
                )

            const dados =
                await resposta.json()

            if (dados.success) {

                location.reload()
c
            } else {

                alert(
                    "Senha incorreta"
                )
            }
        }
    )
}

// MODAL ADMIN
const abrirPainelAdmin =
    document.getElementById(
        "abrir-painel-admin"
    )

// VERIFICA SE O BOTÃO EXISTE ANTES DE ADICIONAR O EVENTO, PARA EVITAR ERROS EM USUÁRIOS QUE NÃO SÃO ADMINISTRADORES
const modalAdmin =
    document.getElementById(
        "modal-admin"
    )

// MESMA VERIFICAÇÃO PARA O BOTÃO DE FECHAR O MODAL
const fecharAdmin =
    document.getElementById(
        "fechar-admin"
    )

// SE O BOTÃO DE ABRIR O PAINEL ADMIN EXISTIR, ADICIONA O EVENTO DE CLIQUE PARA EXIBIR O MODAL
if (abrirPainelAdmin) {

    abrirPainelAdmin.addEventListener(
        "click",
        () => {

            modalAdmin.style.display =
                "flex"
        }
    )
}

//  SE O BOTÃO DE FECHAR EXISTIR, ADICIONA O EVENTO DE CLIQUE PARA OCULTAR O MODAL
if (fecharAdmin) {

    fecharAdmin.addEventListener(
        "click",
        () => {

            modalAdmin.style.display =
                "none"
        }
    )
}

// LOGOUT ADMIN
const logoutAdmin =
    document.getElementById(
        "logout-admin"
    )

if (logoutAdmin) {

    logoutAdmin.addEventListener(
        "click",
        async () => {

            await fetch(
                "/logout-admin"
            )

            alert(
                "Você saiu do modo Admin"
            )

            location.reload()
        }
    )
}

//UPLOAD ADMIN
const formAdmin =
    document.getElementById(
        "form-admin"
    )

if (formAdmin) {

    formAdmin.addEventListener(
        "submit",
        async (e) => {

            e.preventDefault()

            const dados =
                new FormData()

            const imagem =
                document.getElementById(
                    "imagem-agenda"
                ).files[0]
            
            const csv =
                document.getElementById(
                    "csv-agenda"
                ).files[0]

            if (imagem) {

                dados.append(
                    "imagem", 
                    imagem
                )
            }

            if (csv) {

                dados.append(
                    "csv",
                    csv
                )
            }

            const resposta = await fetch(
                "/upload-arquivos",
                {
                    method: "POST",
                    body: dados
                }
            )

            const resultado =
                await resposta.json()

            if (resultado.success) {

                alert(
                    "Arquivos atualizados" 
                )

                location.reload()
            }
        }
    )
}

//CRIAR CHAMADO
document
    .getElementById("form")
    .addEventListener("submit", async (e) => {

        e.preventDefault()

        const formData = new FormData(e.target)

        await fetch("/criar", {
            method: "POST",
            body: formData
        })

        location.reload()
})


// ASSUMIR ATENDIMENTO
document.querySelectorAll(".assumir-btn").forEach((botao) => {

    botao.addEventListener("click", async () => {

        const id = botao.dataset.id

        const linha = botao.closest(".linha")

        const tecnico = linha
            .querySelector(".tecnico-select")
            .value

        if (!tecnico) {

            alert("Selecione um técnico antes de assumir o atendimento.")

            return
        }

        await fetch(`/assumir/${id}`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                tecnico: tecnico
            })

        })

        location.reload()

    })

})


// INICIAR LIGAÇÃO
document.querySelectorAll(".ligacao-btn").forEach((botao) => {

    botao.addEventListener("click", async () => {

        const id = botao.dataset.id

        await fetch(`/contato/${id}`, {
            method: "POST"
        })

        location.reload()

    })

})


// CONTATO REALIZADO
document.querySelectorAll(".contato-btn").forEach((botao) => {

    botao.addEventListener("click", async () => {

        const id = botao.dataset.id

        await fetch(`/contato-realizado/${id}`, {
            method: "POST"
        })

        location.reload()

    })

})


// NÃO ATENDEU
document.querySelectorAll(".nao-atendeu-btn").forEach((botao) => {

    botao.addEventListener("click", async () => {

        const id = botao.dataset.id

        await fetch(`/nao-atendeu/${id}`, {
            method: "POST"
        })

        location.reload()

    })

})


// CONCLUIR
document.querySelectorAll(".concluir-btn").forEach((botao) => {

    botao.addEventListener("click", async () => {

        const id = botao.dataset.id

        await fetch(`/concluir/${id}`, {
            method: "POST"
        })

        location.reload()

    })

})

// SOLICITAR APOIO CHAT
const btnApoio = document.getElementById("btn-apoio-chat")

if (btnApoio) {

    btnApoio.addEventListener(
        "click", 
        async () => {
            await fetch(
                "/solicitar-apoio", 
                {
                    method: "POST"
                }
            )

            location.reload()
    })
}

// DEFINIR APOIO
const confirmaApoio = 
    document.getElementById(
        "confirmar-apoio"
    )

if (confirmaApoio) {

    confirmaApoio.addEventListener(
        "click", 
        async () => {

            const nome = document
                .getElementById(
                    "select-apoio"
                )
                .value
            
            if (!nome) {

                alert(
                    "Selecione um apoio"
                )

                return
            }

            await fetch(
                "/definir-apoio",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        nome: nome
                    })

                }
            )

            location.reload()
        }
    )
}

// ENCERRAR APOIO
const encerrarApoio =
    document.getElementById(
        "encerrar-apoio"
    )

if (encerrarApoio) {

    encerrarApoio.addEventListener(
        "click", 
        async () => {
            await fetch(
                "/encerrar-apoio",
                {
                    method: "POST"
                }
            )

            location.reload()
        }
    )
}

// MODAL AGENDA
const abrirAgenda =
    document.getElementById(
        "abrir-agenda"
    )

const modalAgenda =
    document.getElementById(
        "modal-agenda"
    )

const fecharAgenda =
    document.getElementById(
        "fechar-agenda"
    )

if (abrirAgenda) {

    abrirAgenda.addEventListener(
        "click",
        () => {

            modalAgenda.style.display = "flex"
        }
    )
}

if (fecharAgenda) {

    fecharAgenda.addEventListener(
        "click",
        () => {

            modalAgenda.style.display = "none"
        }
    )
}

// ABRIR LOGIN ADMIN
const abrirAdmin =
    document.getElementById(
        "abrir-admin"
    )

const loginAdminBox =
    document.getElementById(
        "login-admin-box"
    )

if (abrirAdmin) {

    abrirAdmin.addEventListener(
        "click",
        () => {

            loginAdminBox.classList.toggle(
                "mostrar-admin"
            )

        }
    )
}

socket.on("atualizar", () => {
    location.reload()
})