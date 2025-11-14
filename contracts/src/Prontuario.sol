// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title ProntuarioUnificado (esqueleto educacional)
/// @notice Esqueleto para gerenciar referências de prontuários (CID/hash). Não armazena dados sensíveis em texto claro.
contract ProntuarioUnificado {

    address public admin; // dono do sistema (pode ser multisig em produção)

    constructor() {
        admin = msg.sender;
    }

    // --- Roles simples (exemplo mínimo) ---
    mapping(address => bool) public profissionaisAutorizados;
    mapping(address => bool) public pacientesRegistrados;

    modifier somenteAdmin() {
        require(msg.sender == admin, "Somente admin");
        _;
    }

    modifier somenteProfissional() {
        require(profissionaisAutorizados[msg.sender], "Somente profissional autorizado");
        _;
    }

    // --- Modelo de registro: armazenamos referência (CID/hashes) e metadata básica ---
    struct Prontuario {
        address paciente;      // dono lógico
        string cid;            // IPFS CID ou hash do prontuario cifrado
        uint256 updatedAt;     // timestamp da ultima modificação
        address ultimoAutor;   // quem atualizou por ultimo
    }

    // Mapeamento: paciente -> lista de prontuarios por id
    mapping(address => uint256[]) private prontuariosPorPaciente;
    mapping(uint256 => Prontuario) public prontuarios; // id -> registro
    uint256 public nextId = 1;

    // Consentimento: paciente permite que um profissional acesse seus prontuarios
    // (na prática, também poderia ser consentimento off-chain com assinatura)
    mapping(address => mapping(address => bool)) public consentimento; // paciente => (profissional => bool)

    // Events
    event ProntuarioCriado(uint256 indexed id, address indexed paciente, address indexed autor, string cid);
    event ProntuarioAtualizado(uint256 indexed id, address indexed autor, string cid);
    event ConsentimentoAlterado(address indexed paciente, address indexed profissional, bool permitido);
    event ProfissionalAutorizado(address indexed profissional, bool autorizado);

    // --- Admin functions ---
    function setProfissionalAutorizado(address profissional, bool permitido) external somenteAdmin {
        profissionaisAutorizados[profissional] = permitido;
        emit ProfissionalAutorizado(profissional, permitido);
    }

    // Paciente se registra (opcional)
    function registrarPaciente(address paciente) external {
        require(paciente != address(0), "Endereco invalido");
        require(!pacientesRegistrados[paciente], "Paciente ja registrado");

        pacientesRegistrados[paciente] = true;
    }


    // Paciente dá/retira consentimento a um profissional
    function setConsentimento(address profissional, bool permitido) external {
        require(pacientesRegistrados[msg.sender], "Paciente nao registrado");
        consentimento[msg.sender][profissional] = permitido;
        emit ConsentimentoAlterado(msg.sender, profissional, permitido);
    }

    // --- CRUD mínimo ---
    // Cria um novo prontuario (somente profissional autorizado)
    function registrarProntuario(address paciente, string calldata cid) external somenteProfissional returns (uint256) {
        require(pacientesRegistrados[paciente], "Paciente nao registrado");

        // opcional: conferir se profissional tem consentimento (ou paciente pode delegar previamente)
        require(consentimento[paciente][msg.sender] == true, "Profissional sem consentimento do paciente");

        uint256 id = nextId++;
        prontuarios[id] = Prontuario({
            paciente: paciente,
            cid: cid,
            updatedAt: block.timestamp,
            ultimoAutor: msg.sender
        });
        prontuariosPorPaciente[paciente].push(id);

        emit ProntuarioCriado(id, paciente, msg.sender, cid);
        return id;
    }

    // Atualiza uma referência de prontuario — somente profissional autorizado e com consentimento
    function atualizarProntuario(uint256 id, string calldata cid) external somenteProfissional {
        Prontuario storage p = prontuarios[id];
        require(p.paciente != address(0), "Prontuario invalido");
        require(consentimento[p.paciente][msg.sender] == true, "Profissional sem consentimento");
        p.cid = cid;
        p.updatedAt = block.timestamp;
        p.ultimoAutor = msg.sender;
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
