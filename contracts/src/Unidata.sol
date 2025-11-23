// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title Unidata
contract Unidata {

    address public admin; // dono do sistema (pode ser multisig em produção)

    constructor() {
        admin = msg.sender;
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
    modifier somenteAdmin() {
        require(msg.sender == admin, "Somente admin");
        _;
    }

    modifier somenteProfissional() {
        require(profissionaisAutorizados[msg.sender], "Somente profissional autorizado");
        _;
    }

    // --- Eventos ---
    event ProntuarioCriado(uint256 indexed id, address indexed paciente, address indexed autor, string cid);
    event ProntuarioAtualizado(uint256 indexed id, address indexed autor, string cid);
    event ConsentimentoAlterado(address indexed paciente, address indexed profissional, bool permitido);
    event ProfissionalAutorizado(address indexed profissional, bool autorizado);
    event PacienteRegistrado(address paciente);

    // Autorizar profissional
    function setProfissionalAutorizado(address profissional, bool permitido) external somenteAdmin {
        profissionaisAutorizados[profissional] = permitido;
        emit ProfissionalAutorizado(profissional, permitido);
    }

    // Registrar paciente
    function registrarPaciente(address paciente) external {
        require(paciente != address(0), "Endereco invalido");
        require(!pacientesRegistrados[paciente], "Paciente ja registrado");

        pacientesRegistrados[paciente] = true;

        emit PacienteRegistrado(paciente);
    }

    // Paciente dá/retira consentimento a um profissional
    function setConsentimento(address paciente, address profissional, bool permitido) external {
        require(pacientesRegistrados[paciente], "Paciente nao registrado");
        consentimento[paciente][profissional] = permitido;
        emit ConsentimentoAlterado(paciente, profissional, permitido);
    }

    // Cria um novo prontuario (somente profissional autorizado)
    function registrarProntuario(address paciente, string calldata cid, address profissional) external somenteProfissional returns (uint256) {
        require(pacientesRegistrados[paciente], "Paciente nao registrado");

        require(consentimento[paciente][profissional] == true, "Profissional sem consentimento do paciente");

        uint256 id = nextId++;
        prontuarios[id] = Prontuario({
            paciente: paciente,
            cid: cid,
            updatedAt: block.timestamp,
            ultimoAutor: profissional
        });
        prontuariosPorPaciente[paciente].push(id);

        emit ProntuarioCriado(id, paciente, msg.sender, cid);
        return id;
    }

    // Atualiza uma referência de prontuario — somente profissional autorizado e com consentimento
    function atualizarProntuario(uint256 id, string calldata cid, address profissional) external somenteProfissional {
        Prontuario storage p = prontuarios[id];

        require(p.paciente != address(0), "Prontuario invalido");
        require(consentimento[p.paciente][profissional] == true, "Profissional sem consentimento");

        p.cid = cid;
        p.updatedAt = block.timestamp;
        p.ultimoAutor = profissional;
        emit ProntuarioAtualizado(id, msg.sender, cid);
    }

    // Leitura: lista de IDs para um paciente (público para simplicidade; em prod restrinja)
    function listarProntuarios(address paciente) external view returns (uint256[] memory) {
        return prontuariosPorPaciente[paciente];
    }

    // Leitura: obter metadados de um prontuario
    function getProntuario(uint256 id) external view returns (address paciente, string memory cid, uint256 updatedAt, address ultimoAutor) {
        Prontuario storage p = prontuarios[id];
        return (p.paciente, p.cid, p.updatedAt, p.ultimoAutor);
    }
}
