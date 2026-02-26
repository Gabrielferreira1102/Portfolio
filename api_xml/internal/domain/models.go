package domain

import (
	"encoding/xml"
	"errors"
	"time"
)

// ========== Veículos e Interfaces ==========
type Requisicao struct {
	Placa string `json:"placa"`
}

type ProdutoBasicoRow struct {
	IDItem   int64  `json:"id_item"`
	NomItem  string `json:"nom_item"`
	BarCode  string `json:"bar_code"`
	FabCode  string `json:"fab_code"`
	Marca    string `json:"marca"`
	ItemCat  string `json:"item_cat"`
	PrVenda  int64  `json:"pr_venda"`
	ProdEst  int64  `json:"prod_est"`
	FornNom  string `json:"forn_nom"`
	ForCnpj  string `json:"for_cnpj"`
	ItemVenc any    `json:"item_venc"` // pode vir como time/NULL
}

type ProdutoCompletoRow struct {
	IDItem int64 `json:"id_item"`

	// est_basico
	NomItem  string `json:"nom_item"`
	BarCode  string `json:"bar_code"`
	FabCode  string `json:"fab_code"`
	ForCnpj  string `json:"for_cnpj"`
	Marca    string `json:"marca"`
	ItemCat  string `json:"item_cat"`
	ItemVenc any    `json:"item_venc"`
	FornNom  string `json:"forn_nom"`
	NfeChave string `json:"nfe_chave"`
	PrVenda  int64  `json:"pr_venda"`
	ProdEst  int64  `json:"prod_est"`
	FkLoj    int64  `json:"fk_numloj_id"`
	FkUsu    int64  `json:"fk_numusu_id"`
}

type ProdutoFront struct {
	IDItem      int64  `json:"id_item"`
	EstBasicoID int64  `json:"est_basico_id"`
	ItemCat     string `json:"item_cat"`
	Marca       string `json:"marca"`
	PrVenda     int64  `json:"pr_venda"`
	Modo        bool   `json:"modo"`
}

// DadosIniciais representa os dados iniciais para criar um orçamento
type DadosIniciais struct {
	TipoCliente string `json:"tipo_cliente" validate:"nonzero"`
	NomeCliente string `json:"nome_cliente"`
	NomeVeiculo string `json:"nome_veiculo"`
	FKCliente   int64  `json:"fk_cliente"`
	FKVeiculo   int64  `json:"fk_veiculo"`
	FKLojaID    int64  `json:"fk_numloj_id" validate:"nonzero"`
}

// ProdutoBuscaRequest representa a requisição de busca de produtos
type ProdutoBuscaRequest struct {
	InputBusca string `json:"input_busca"`
}

// ProdutoAdicionar representa os dados para adicionar um produto a um orçamento
type ProdutoAdicionar struct {
	IDProduto  int64  `json:"id_produto" validate:"nonzero"`
	Quantidade int16  `json:"quantidade"`
	Preco      string `json:"preco"`
	DescPerc   int64  `json:"desc_perc"`
	DescNom    int64  `json:"desc_nom"`
	FKLojaID   int64  `json:"fk_numloj_id" validate:"nonzero"`
}

type Veiculo struct {
	Placa       string `json:"placa"`
	Marca       string `json:"marca"`
	Modelo      string `json:"modelo"`
	SubModel    string `json:"sub_model"`
	AnoFab      string `json:"ano_fab"`
	AnoMod      string `json:"ano_mod"`
	Combustivel string `json:"combustivel"`
	Cor         string `json:"cor"`
	Geracao     string `json:"geracao"`
	TipoVeiculo string `json:"tip_veic"`
	Frota       string `json:"frota"`
	Chassi      string `json:"chassi"`
}

type Veiculos struct {
	IdCar      int    `json:"id_car"`
	IdPlaca    string `json:"id_placa"`
	Marca      string `json:"car_marca"`
	NomeModelo string `json:"mod_nome"`
	Car_comb   string `json:"car_comb"`
	Fab_ano    string `json:"fab_ano"`
	Mod_ano    string `json:"mod_ano"`
	Car_cor    string `json:"car_cor"`
	Car_tip    string `json:"car_tip"`
	Car_chassi string `json:"car_chassi"`
	Frota      bool   `json:"car_frota"`
	For_loj    int    `json:"for_loj"`
	For_cli    int    `json:"for_cli"`
}

type PlacaUsecase interface {
	BuscarPorPlaca(placa string) (*Veiculo, error)
}

type PlacaRepository interface {
	FindByPlaca(placa string) (*Veiculo, error)
}

// ========== Fornecedor, Cliente, Serviço ==========
type Fornecedor struct {
	ID         int    `json:"id_f"`
	Nome       string `json:"f_nome"`
	Telefone   string `json:"f_tel"`
	Celular    string `json:"f_cel"`
	Email      string `json:"f_email"`
	CEP        string `json:"f_cep"`
	Logradouro string `json:"f_logradouro"`
	Numero     int    `json:"f_num"`
	UF         string `json:"f_uf"`
	Cidade     string `json:"f_cidade"`
	Bairro     string `json:"f_bairro"`
	Setor      string `json:"f_setor"`
	Categoria  string `json:"f_categoria"`
	LojaID     int    `json:"for_loj"`
}

type ClientePF struct {
	ID            int    `json:"id_client"`
	Nome          string `json:"cli_nome"`
	Tipo          string `json:"cli_tip"`
	CPF           string `json:"cli_cpf"`
	DataCadastro  string `json:"cad_data"`
	QtdServicos   int    `json:"cli_serv"`
	Locador       bool   `json:"cli_loc"`
	Nacionalidade string `json:"cli_nac"`
	Genero        string `json:"cli_gen"`
	EstadoCivil   string `json:"cli_civil"`
	Nascimento    string `json:"dat_nac"`
	AutDados      bool   `json:"lgpd_aut"`
	ComoConheceu  string `json:"com_con"`
	IsencaoISS    bool   `json:"i_iss"`
	RetencaoIRFF  bool   `json:"ret_irff"`
	Obs           string `json:"cli_obs"`
	LojaID        int    `json:"for_loj"`
}

type EnderecoCliente struct {
	IDEndereco int    `json:"id_end"`
	CEP        string `json:"end_cep"`
	Logradouro string `json:"end_logradouro"`
	Numero     string `json:"end_num"`
	UF         string `json:"end_uf"`
	Cidade     string `json:"end_cidade"`
	Bairro     string `json:"end_bairro"`
	Entrega    bool   `json:"end_ent"`
	Principal  bool   `json:"end_principal"`
	LojaID     int    `json:"for_loj"`
	ClienteID  int    `json:"for_cli"`
}

type StockProd struct {
	ProdID     int64  `json:"prod_id"`
	Type       bool   `json:"type"`
	EANGTIN    string `json:"ean_gtin"`
	SKUInterno string `json:"sku_interno"`
	UnitMedida string `json:"unit_medida"`
	ProdName   string `json:"prod_name"`
	FracAllow  bool   `json:"frac_allow"`
	XProd      string `json:"xprod"`
	ProdPrice  int64  `json:"prod_price"`
	ProdStock  int64  `json:"prod_stock"`
	FKNumLojID int64  `json:"fk_numlojid"`
}

type StockMove struct {
	StockMovID int64     `json:"stockmov_id"`
	NumLojID   int64     `json:"numlojid"`
	ProdID     int64     `json:"prodid"`
	MoveType   int16     `json:"move_type"`
	DirMove    int64     `json:"dir_move"`
	Quant      float64   `json:"quant"`
	UnitPrice  int64     `json:"unit_price"`
	Balance    float64   `json:"balance"`
	OrcID      *int64    `json:"orc_id"`
	CreatedAt  time.Time `json:"created_at,omitempty"`
}

type ContatosCliente struct {
	IDContato    int    `json:"id_contato"`
	TipoContato  int    `json:"cont_tipo"`
	Contato_info string `json:"cont_info"`
	ClienteID    int    `json:"for_cli"`
	LojaID       int    `json:"for_loj"`
}

type Servico struct {
	IDServico      int    `json:"id_serv"`
	Serv_nome      string `json:"serv_nom"`
	Serv_codigo    string `json:"serv_cod"`
	Serv_descricao string `json:"serv_desc"`
	Serv_valor     int64  `json:"serv_val"`
	Serv_bc        int64  `json:"serv_bc"`
	Serv_op_iss    bool   `json:"serv_op_iss"`
	Serv_iss       int64  `json:"serv_iss"`
	For_loj        int    `json:"for_loj"`
}

// ========== Duplicata e Resultado XML ==========
type DuplicataEstoque struct {
	SIDItem   int64  `json:"id_item"`     // ID do est_basico
	SNomItem  string `json:"nom_item"`    // Nome do item
	SBarCode  string `json:"bar_code"`    // Código de barras
	SCodEAN   string `json:"cod_ean"`     // Código EAN
	SProdEst  int64  `json:"prod_est"`    // Quantidade no estoque
	SPrVenda  int64  `json:"pr_venda"`    // Preço de venda
	XMLItemID int64  `json:"xml_item_id"` // Novo campo para o ID do item no XML
}

type ResultadoProduto struct {
	ProdutoXML       ProdutoNFe        `json:"produto_xml"`
	DuplicataEstoque *DuplicataEstoque `json:"duplicata_estoque,omitempty"`
}

// ========== XML da NF-e ==========
type NFeProc struct {
	XMLName xml.Name `xml:"nfeProc"`
	NFe     NFeXML   `xml:"NFe"`
}

type NFeXML struct {
	XMLName xml.Name `xml:"NFe"`
	InfNFe  struct {
		ID   string    `xml:"Id,attr" json:"id"`
		Emit Emitente  `xml:"emit" json:"emit"`
		Det  []Detalhe `xml:"det" json:"det"`
	} `xml:"infNFe" json:"inf_nfe"`
}

// Função para fazer o parse do XML da NF-e
func ParseNFeXML(data []byte) (NFeXML, error) {
	var nfe NFeXML
	err := xml.Unmarshal(data, &nfe)
	if err != nil {
		return nfe, errors.New("erro ao fazer o parse do XML")
	}
	return nfe, nil
}

type InfNFe struct {
	ID   string    `xml:"Id,attr"`
	Emit Emitente  `xml:"emit"`
	Det  []Detalhe `xml:"det"`
}

type Emitente struct {
	FOR_CNPJ string `xml:"CNPJ"`
	FORN_NOM string `xml:"xNome"`
}

type Detalhe struct {
	Prod    Produto `xml:"prod"`
	Imposto Imposto `xml:"imposto"`
}

type EST_BASICO struct {
	NOM_ITEM     string `json:"nom_item"`
	BAR_CODE     string `json:"bar_code"`
	COD_EAN      string `json:"cod_ean"`
	FAB_CODE     string `json:"fab_code"`
	FOR_CNPJ     string `json:"for_cnpj"`
	FORN_NOM     string `json:"forn_nom"`
	NFE_CHAVE    string `json:"nfe_chave"`
	PR_VENDA     int64  `json:"pr_venda"`
	PROD_EST     int64  `json:"prod_est"`
	ITEM_CAT     string `json:"item_cat"`
	MARCA        string `json:"marca"`
	ITEM_VENC    string `json:"item_venc"`
	Fk_numloj_id int64  `json:"Fk_numloj_id"`
	Fk_numusu_id int64  `json:"Fk_numusu_id"`
}

type DFB_ESTOQUE struct {
	COD_EAN     string `json:"COD_EAN"`
	COD_NCM     string `json:"COD_NCM"`
	COD_CEST    string `json:"COD_CEST"`
	COD_CFOP    string `json:"COD_CFOP"`
	UN_COM      string `json:"UN_COM"`
	UN_TRIB     string `json:"UN_TRIB"`
	QTD_COM     string `json:"QTD_COM"`
	VAL_UN_COM  string `json:"VAL_UN_COM"`
	VAL_UN_TRIB string `json:"VAL_UN_TRIB"`
}

type DICMS_ESTOQUE struct {
	ORIGEM     string  `json:"origem"`
	CST        string  `json:"cst"`
	V_BC       float64 `json:"v_bc"`
	P_ICMS     float64 `json:"p_icms"`
	V_ICMS     float64 `json:"v_icms"`
	P_MVAST    float64 `json:"p_mvast"`
	P_RED_BCST float64 `json:"p_red_bcst"`
	V_BCST     float64 `json:"v_bcst"`
	P_ICMS_ST  float64 `json:"p_icms_st"`
	V_ICMS_ST  float64 `json:"v_icms_st"`
	MOD_BC     string  `json:"mod_bc"`
	MOD_BC_ST  string  `json:"mod_bc_st"`
}

type DIMP_ESTOQUE struct {
	VAL_ADUANEIRO  string `json:"val_aduaneiro"`
	VAL_BASE_CALC  string `json:"val_base_calc"`
	VAL_IMPOSTO    string `json:"val_imposto"`
	COD_EXPORTADOR string `json:"cod_exportador"`
}

type DPIS_ESTOQUE struct {
	PIS_CST    string `json:"pis_cst"`
	PIS_V_BC   string `json:"pis_v_bc"`
	PIS_P_ALIQ string `json:"pis_p_aliq"`
	PIS_V_PIS  string `json:"pis_v_pis"`
}

type DCOFINS_ESTOQUE struct {
	COFINS_CST      string `json:"cofins_cst"`
	COFINS_V_BC     string `json:"cofins_v_bc"`
	COFINS_P_ALIQ   string `json:"cofins_p_aliq"`
	COFINS_V_COFINS string `json:"cofins_v_cofins"`
}

type DCOMB_ESTOQUE struct {
	COD_P_ANP     string `json:"cod_p_anp"`
	PERC_G_GLP    string `json:"perc_g_glp"`
	COD_AUT       string `json:"cod_aut"`
	UF_CONSUMO    string `json:"uf_consumo"`
	CIDE_BC       string `json:"cide_bc"`
	ALIQ_CIDE     string `json:"aliq_cide"`
	VAL_CIDE      string `json:"val_cide"`
	DESC_PROD_ANP string `json:"desc_prod_anp"`
	P_GNN         string `json:"p_gnn"`
	P_GNI         string `json:"p_gni"`
}

type DDI_ESTOQUE struct {
	COD_EIPI string `json:"cod_eipi"`
	ST_IPI   string `json:"st_ipi"`
	CLSS_ENQ string `json:"clss_enq"`
	ALIQ_IPI string `json:"aliq_ipi"`
	VAL_IPI  string `json:"val_ipi"`
}

type Produto struct {
	NOM_ITEM      string `xml:"xProd" json:"nom_item"`
	BAR_CODE      string `xml:"cEAN" json:"bar_code"`
	FAB_CODE      string `xml:"cProd" json:"fab_code"`
	NCM           string `xml:"NCM" json:"ncm"`
	CFOP          string `xml:"CFOP" json:"cfop"`
	UN_COM        string `xml:"uCom" json:"un_com"`
	UN_TRIB       string `xml:"uTrib" json:"un_trib"`
	QTD_COM       string `xml:"qCom" json:"qtd_com"`
	VAL_UN_COM    string `xml:"vUnCom" json:"val_un_com"`
	VAL_UN_TRIB   string `xml:"vUnTrib" json:"val_un_trib"`
	MARCA         string `xml:"xMarca" json:"marca"`
	ITEM_CAT      string `xml:"cCEST" json:"item_cat"`
	ITEM_VENC     string `xml:"dVal" json:"item_venc"`
	COD_P_ANP     string `xml:"cProdANP" json:"cod_p_anp"`
	PERC_G_GLP    string `xml:"pGLP" json:"perc_g_glp"`
	COD_AUT       string `xml:"COD_AUT" json:"cod_aut"`
	UF_CONSUMO    string `xml:"UF" json:"uf_consumo"`
	CIDE_BC       string `xml:"qBCProd" json:"cide_bc"`
	ALIQ_CIDE     string `xml:"vAliqProd" json:"aliq_cide"`
	VAL_CIDE      string `xml:"vCIDE" json:"val_cide"`
	DESC_PROD_ANP string `xml:"descANP" json:"desc_prod_anp"`
	P_GNN         string `xml:"pGNn" json:"p_gnn"`
	P_GNI         string `xml:"pGNi" json:"p_gni"`
}

type Imposto struct {
	DICMS_ESTOQUE   DICMS_ESTOQUE   `xml:"ICMS"`
	DIMP_ESTOQUE    DIMP_ESTOQUE    `xml:"II"`
	DPIS_ESTOQUE    DPIS_ESTOQUE    `xml:"PIS"`
	DCOFINS_ESTOQUE DCOFINS_ESTOQUE `xml:"COFINS"`
	DDI_ESTOQUE     DDI_ESTOQUE     `xml:"IPI"`
}

type ProdutoNFe struct {
	ID              int64            `json:"id"`
	EST_BASICO      EST_BASICO       `json:"EST_BASICO"`
	DFB_ESTOQUE     *DFB_ESTOQUE     `json:"DFB_ESTOQUE,omitempty"`
	DICMS_ESTOQUE   *DICMS_ESTOQUE   `json:"DICMS_ESTOQUE,omitempty"`
	DIMP_ESTOQUE    *DIMP_ESTOQUE    `json:"DIMP_ESTOQUE,omitempty"`
	DPIS_ESTOQUE    *DPIS_ESTOQUE    `json:"DPIS_ESTOQUE,omitempty"`
	DCOFINS_ESTOQUE *DCOFINS_ESTOQUE `json:"DCOFINS_ESTOQUE,omitempty"`
	DCOMB_ESTOQUE   *DCOMB_ESTOQUE   `json:"DCOMB_ESTOQUE,omitempty"`
	DDI_ESTOQUE     *DDI_ESTOQUE     `json:"DDI_ESTOQUE,omitempty"`
	FK_NUMLOJ_ID    int64            `json:"FK_NUMLOJ_ID"`
	FK_NUMUSU_ID    int64            `json:"FK_NUMUSU_ID"`
	USER            string           `json:"USER"`
}

type TabXML struct {
	IDItem  int64  `json:"id_item"`
	NomItem string `json:"nom_item"`
	BarCode string `json:"bar_code"`
	CodEAN  string `json:"cod_ean"`
	ProdEst int64  `json:"prod_est"`
	PrVenda int64  `json:"pr_venda"`
}
