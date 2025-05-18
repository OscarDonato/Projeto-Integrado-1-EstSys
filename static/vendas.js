async function buscarCliente() {
    const cpf = document.getElementById("cpf").value.trim();

    if (cpf.length < 3) {
      document.getElementById("resultadoCliente").textContent = "";  // limpa se pouco texto
      document.querySelector("input[name='cli_nome']").value = "";
      document.querySelector("input[name='cli_doc']").value = "";
      return;
    }

    try {
      const resp = await fetch(`/buscar_cliente?cpf=${encodeURIComponent(cpf)}`);
      const data = await resp.json();

      if (resp.ok) {
        document.querySelector("input[name='cli_nome']").value = data.nome;
        document.querySelector("input[name='cli_doc']").value = data.doc;
        document.getElementById("resultadoCliente").textContent =
          `Nome: ${data.nome} | Telefone: ${data.telefone}`;
      } else {
        document.querySelector("input[name='cli_nome']").value = '';
        document.querySelector("input[name='cli_doc']").value = '';
        document.getElementById("resultadoCliente").textContent = "Cliente não encontrado";
      }
    } catch {
      document.getElementById("resultadoCliente").textContent = "Erro ao buscar cliente";
    }
  }