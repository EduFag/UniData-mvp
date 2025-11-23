// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title Unidata
contract Unidata {

    address public admin; // dono do sistema (pode ser multisig em produção)
    address public apiSigner;  // Carteira do Backend que paga o GAS

    constructor() {
        admin = msg.sender;
        apiSigner = msg.sender;
    }

    // Estrutura de registro
    struct Prontuario {
        address paciente;      // dono lógico
        string cid;            // CID do prontuario cifrado
        uint256 updatedAt;     // timestamp da ultima modificação
        address ultimoAutor;   // quem atualizou por ultimo
    }

    // --- Armazenamento ---
    mapping(address => bool) public profissionaisAutorizados;
    mapping(address => bool) public pacientesRegistrados;

    mapping(address => uint256[]) private prontuariosPorPaciente;
    mapping(uint256 => Prontuario) public prontuarios; // id -> registro
    uint256 public nextId = 1;

    mapping(address => mapping(address => bool)) public consentimento; // paciente => (profissional => bool)

    // --- Modificadores ---
    modifier somenteApi() {
        require(msg.sender == apiSigner, "Acesso negado: Somente API");
        _;
    }

    modifier somenteAdmin() {
        require(msg.sender == admin, "Somente admin");
        _;
    }

    // --- Eventos ---
    event ProntuarioCriado(uint256 indexed id, address indexed paciente, address indexed autorMedico, string cid);
    event ProntuarioAtualizado(uint256 indexed id, address indexed autorMedico, string cid);
    event ConsentimentoAlterado(address indexed paciente, address indexed profissional, bool permitido);
    event ProfissionalAutorizado(address indexed profissional, bool autorizado);
    event PacienteRegistrado(address paciente);
    event ApiSignerAtualizado(address novoSigner);

    // Permite trocar a carteira da API
    function setApiSigner(address _novoSigner) external somenteAdmin {
        apiSigner = _novoSigner;
        emit ApiSignerAtualizado(_novoSigner);
    }

    // Autorizar profissional
    function setProfissionalAutorizado(address profissional, bool permitido) external somenteAdmin {
        profissionaisAutorizados[profissional] = permitido;
        emit ProfissionalAutorizado(profissional, permitido);
    }

    // Registrar paciente
    function registrarPaciente(address paciente) external somenteApi {
        require(paciente != address(0), "Endereco invalido");
        require(!pacientesRegistrados[paciente], "Paciente ja registrado");

        pacientesRegistrados[paciente] = true;
        emit PacienteRegistrado(paciente);
    }

    // Paciente dá/retira consentimento a um profissional
    function setConsentimento(address paciente, address profissional, bool permitido) external somenteApi {
        require(pacientesRegistrados[paciente], "Paciente nao registrado");
        
        consentimento[paciente][profissional] = permitido;
        emit ConsentimentoAlterado(paciente, profissional, permitido);
    }

    function criarProntuario(address paciente, string calldata cid, address profissional) external somenteApi returns (uint256) {
        require(pacientesRegistrados[paciente], "Paciente nao registrado");
        
        // Validação On-Chain: O endereço passado como médico é realmente um médico autorizado?
        require(profissionaisAutorizados[profissional], "O endereco fornecido nao eh de um medico autorizado");

        // Validação On-Chain: O paciente deu permissão para ESTE médico?
        require(consentimento[paciente][profissional] == true, "Medico sem consentimento do paciente");

        uint256 id = nextId++;
        prontuarios[id] = Prontuario({
            paciente: paciente,
            cid: cid,
            updatedAt: block.timestamp,
            ultimoAutor: profissional // Registramos o médico, não a API
        });
        prontuariosPorPaciente[paciente].push(id);

        // Emitimos o evento com o endereço do médico para indexação correta
        emit ProntuarioCriado(id, paciente, profissional, cid);
        return id;
    }

    function atualizarProntuario(uint256 id, string calldata cid, address profissional) external somenteApi {
        Prontuario storage p = prontuarios[id];

        require(p.paciente != address(0), "Prontuario nao existe");
        require(profissionaisAutorizados[profissional], "Endereco nao eh medico");
        require(consentimento[p.paciente][profissional] == true, "Medico sem consentimento");

        p.cid = cid;
        p.updatedAt = block.timestamp;
        p.ultimoAutor = profissional;
        
        emit ProntuarioAtualizado(id, profissional, cid);
    }

    // --- Leitura (Públicas ou Restritas a View) ---
    // Funções de leitura não gastam gás, podem ser chamadas direto pelo Frontend ou via API
    
    function listarProntuarios(address paciente) external view returns (uint256[] memory) {
        return prontuariosPorPaciente[paciente];
    }

    function getProntuario(uint256 id) external view returns (address paciente, string memory cid, uint256 updatedAt, address ultimoAutor) {
        Prontuario storage p = prontuarios[id];
        return (p.paciente, p.cid, p.updatedAt, p.ultimoAutor);
    }
}
