package handler

import (
	"encoding/json"
	"encoding/xml"
	"io/ioutil"
	"mime/multipart"
	"net/http"
	"projeto_troca_de_oleo/internal/domain"
	"projeto_troca_de_oleo/internal/repository"
	"strconv"

	"github.com/gin-gonic/gin"
)

func RegisterProdutoNFeRoutes(router *gin.Engine, repo *repository.ProdutoNFeRepository) {
	router.POST("/api/produto-nfe", func(c *gin.Context) {
		formFile, _, err := c.Request.FormFile("file")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"erro": "Arquivo não recebido", "detalhe": err.Error()})
			return
		}
		defer formFile.Close()

		byteValue, err := readAll(formFile)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"erro": "Erro ao ler o arquivo", "detalhe": err.Error()})
			return
		}

		var nfe domain.NFeXML

		err = xml.Unmarshal(byteValue, &nfe)
		if err != nil || nfe.InfNFe.ID == "" {
			var proc domain.NFeProc
			err = xml.Unmarshal(byteValue, &proc)
			if err != nil {
				c.JSON(http.StatusBadRequest, gin.H{"erro": "Erro ao processar o XML", "detalhe": err.Error()})
				return
			}
			nfe = proc.NFe
		}

		for _, det := range nfe.InfNFe.Det {
			if repository.TemSQLInjection(det.Prod.NOM_ITEM) || repository.TemSQLInjection(det.Prod.FAB_CODE) {
				c.JSON(http.StatusBadRequest, gin.H{"erro": "Possível SQL Injection detectado"})
				return
			}
		}

		type ProdutoComID struct {
			ID int64 `json:"id"`
			domain.ProdutoNFe
		}

		var produtos []ProdutoComID

		for i, det := range nfe.InfNFe.Det {
			prVenda, _ := strconv.ParseFloat(det.Prod.VAL_UN_COM, 64)
			prodEst, _ := strconv.ParseFloat(det.Prod.QTD_COM, 64)

			produto := ProdutoComID{
				ID: int64(i + 1),
				ProdutoNFe: domain.ProdutoNFe{
					ID: int64(i + 1), // Adiciona o ID ao ProdutoNFe para uso em VerificarDuplicatasGo
					EST_BASICO: domain.EST_BASICO{
						NOM_ITEM:     det.Prod.NOM_ITEM,
						BAR_CODE:     det.Prod.BAR_CODE,
						COD_EAN:      det.Prod.BAR_CODE, // Usar BAR_CODE como COD_EAN, conforme estrutura de resposta esperada
						FAB_CODE:     det.Prod.FAB_CODE,
						MARCA:        det.Prod.MARCA,
						ITEM_CAT:     det.Prod.ITEM_CAT,
						ITEM_VENC:    det.Prod.ITEM_VENC,
						FOR_CNPJ:     nfe.InfNFe.Emit.FOR_CNPJ,
						FORN_NOM:     nfe.InfNFe.Emit.FORN_NOM,
						NFE_CHAVE:    nfe.InfNFe.ID,
						PR_VENDA:     int64(prVenda),
						PROD_EST:     int64(prodEst),
						Fk_numloj_id: 1,
						Fk_numusu_id: 999,
					},
					DFB_ESTOQUE: &domain.DFB_ESTOQUE{
						COD_EAN:     det.Prod.BAR_CODE,
						COD_NCM:     det.Prod.NCM,
						COD_CEST:    det.Prod.ITEM_CAT,
						COD_CFOP:    det.Prod.CFOP,
						UN_COM:      det.Prod.UN_COM,
						UN_TRIB:     det.Prod.UN_TRIB,
						QTD_COM:     det.Prod.QTD_COM,
						VAL_UN_COM:  det.Prod.VAL_UN_COM,
						VAL_UN_TRIB: det.Prod.VAL_UN_TRIB,
					},
					DICMS_ESTOQUE: &domain.DICMS_ESTOQUE{
						ORIGEM:     det.Imposto.DICMS_ESTOQUE.ORIGEM,
						CST:        det.Imposto.DICMS_ESTOQUE.CST,
						V_BC:       det.Imposto.DICMS_ESTOQUE.V_BC,
						P_ICMS:     det.Imposto.DICMS_ESTOQUE.P_ICMS,
						V_ICMS:     det.Imposto.DICMS_ESTOQUE.V_ICMS,
						P_MVAST:    det.Imposto.DICMS_ESTOQUE.P_MVAST,
						P_RED_BCST: det.Imposto.DICMS_ESTOQUE.P_RED_BCST,
						V_BCST:     det.Imposto.DICMS_ESTOQUE.V_BCST,
						P_ICMS_ST:  det.Imposto.DICMS_ESTOQUE.P_ICMS_ST,
						V_ICMS_ST:  det.Imposto.DICMS_ESTOQUE.V_ICMS_ST,
						MOD_BC:     det.Imposto.DICMS_ESTOQUE.MOD_BC,
						MOD_BC_ST:  det.Imposto.DICMS_ESTOQUE.MOD_BC_ST,
					},
					DIMP_ESTOQUE:    &det.Imposto.DIMP_ESTOQUE,
					DPIS_ESTOQUE:    &det.Imposto.DPIS_ESTOQUE,
					DCOFINS_ESTOQUE: &det.Imposto.DCOFINS_ESTOQUE,
					DCOMB_ESTOQUE: &domain.DCOMB_ESTOQUE{
						COD_P_ANP:     det.Prod.COD_P_ANP,
						PERC_G_GLP:    det.Prod.PERC_G_GLP,
						COD_AUT:       det.Prod.COD_AUT,
						UF_CONSUMO:    det.Prod.UF_CONSUMO,
						CIDE_BC:       det.Prod.CIDE_BC,
						ALIQ_CIDE:     det.Prod.ALIQ_CIDE,
						VAL_CIDE:      det.Prod.VAL_CIDE,
						DESC_PROD_ANP: det.Prod.DESC_PROD_ANP,
						P_GNN:         det.Prod.P_GNN,
						P_GNI:         det.Prod.P_GNI,
					},
					DDI_ESTOQUE:  &det.Imposto.DDI_ESTOQUE,
					FK_NUMLOJ_ID: 1,
					FK_NUMUSU_ID: 999,
					USER:         "admin",
				},
			}
			produtos = append(produtos, produto)
		}

		jsonData, err := json.MarshalIndent(produtos, "", "  ")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"erro": "Erro ao gerar JSON", "detalhe": err.Error()})
			return
		}

		jsonID, err := repo.SalvarJSONComoArquivo(jsonData)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"erro": "Erro ao salvar JSON no banco", "detalhe": err.Error()})
			return
		}

		// Extrair somente os ProdutoNFe para verificar duplicatas
		var produtosSomente []domain.ProdutoNFe
		for _, p := range produtos {
			produtosSomente = append(produtosSomente, p.ProdutoNFe)
		}

		duplicatas := repo.VerificarDuplicatasGo(produtosSomente)

		// Construir tab_xml para a resposta
		var produtosXML []domain.TabXML
		for _, p := range produtos {
			tab := domain.TabXML{
				IDItem:  p.ID,
				NomItem: p.EST_BASICO.NOM_ITEM,
				BarCode: p.EST_BASICO.FAB_CODE, // Usar FAB_CODE como bar_code, conforme resposta esperada
				CodEAN:  p.EST_BASICO.BAR_CODE, // Usar BAR_CODE como cod_ean, conforme resposta esperada
				ProdEst: p.EST_BASICO.PROD_EST,
				PrVenda: p.EST_BASICO.PR_VENDA,
			}
			produtosXML = append(produtosXML, tab)
		}

		// Mapear duplicatas para a estrutura de resposta
		var duplicatasResponse []struct {
			IDItem    int64  `json:"id_item"`
			NomItem   string `json:"nom_item"`
			BarCode   string `json:"bar_code"`
			CodEAN    string `json:"cod_ean"`
			ProdEst   int64  `json:"prod_est"`
			PrVenda   int64  `json:"pr_venda"`
			XMLItemID int64  `json:"xml_item_id"`
		}
		for _, d := range duplicatas {
			duplicatasResponse = append(duplicatasResponse, struct {
				IDItem    int64  `json:"id_item"`
				NomItem   string `json:"nom_item"`
				BarCode   string `json:"bar_code"`
				CodEAN    string `json:"cod_ean"`
				ProdEst   int64  `json:"prod_est"`
				PrVenda   int64  `json:"pr_venda"`
				XMLItemID int64  `json:"xml_item_id"`
			}{
				IDItem:    d.SIDItem,
				NomItem:   d.SNomItem,
				BarCode:   d.SBarCode,
				CodEAN:    d.SCodEAN,
				ProdEst:   d.SProdEst,
				PrVenda:   d.SPrVenda,
				XMLItemID: d.XMLItemID,
			})
		}

		c.JSON(http.StatusOK, gin.H{
			"id_json":            jsonID,
			"tab_xml":            produtosXML,
			"duplicatas_estoque": duplicatasResponse,
		})
	})
}

func readAll(file multipart.File) ([]byte, error) {
	return ioutil.ReadAll(file)
}
