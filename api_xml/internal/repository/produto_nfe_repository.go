package repository

import (
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"os"
	"projeto_troca_de_oleo/internal/domain"
	"strings"
)

type ProdutoNFeRepository struct {
	db *sql.DB
}

func NewProdutoNFeRepository(db *sql.DB) *ProdutoNFeRepository {
	log.SetOutput(os.Stdout)
	return &ProdutoNFeRepository{db: db}
}

// Salva o JSON corretamente como um array de objetos e retorna id_json
func (r *ProdutoNFeRepository) SalvarJSONComoArquivo(jsonData []byte) (int, error) {
	var id int
	query := `INSERT INTO temp_json (t_json, created_at) VALUES ($1, NOW()) RETURNING id_json`
	err := r.db.QueryRow(query, jsonData).Scan(&id)
	if err != nil {
		return 0, fmt.Errorf("erro ao inserir JSON: %w", err)
	}
	return id, nil
}

// Verifica se contém tentativa de SQL injection simples
func TemSQLInjection(input string) bool {
	injectionPatterns := []string{
		"' OR '1'='1", "--", ";--", "';--", "' or '1'='1",
		"DROP TABLE", "SELECT *", "INSERT INTO", "DELETE FROM", "UPDATE SET",
	}
	upperInput := strings.ToUpper(input)
	for _, pattern := range injectionPatterns {
		if strings.Contains(upperInput, pattern) {
			return true
		}
	}
	return false
}

// Verifica duplicatas no banco com base nos dados de produtos
func (r *ProdutoNFeRepository) VerificarDuplicatasGo(produtos []domain.ProdutoNFe) []domain.DuplicataEstoque {
	log.Println("[DEBUG] Iniciando verificação de duplicatas")

	var duplicatas []domain.DuplicataEstoque

	for _, prod := range produtos {
		barCode := prod.EST_BASICO.BAR_CODE
		codEAN := prod.EST_BASICO.COD_EAN
		nomItem := prod.EST_BASICO.NOM_ITEM
		xmlItemID := prod.ID // ID do item no XML

		log.Printf("[DEBUG] Verificando produto -> Nome: %s | BAR_CODE: %s | EAN: %s | XML Item ID: %d", nomItem, barCode, codEAN, xmlItemID)

		if barCode == "" && codEAN == "" && nomItem == "" {
			log.Println("[DEBUG] Produto com todos os campos vazios. Pulando...")
			continue
		}

		query := `
            SELECT eb.id_item, eb.nom_item, eb.bar_code, COALESCE(dfb.cod_ean, '') as cod_ean, 
                   eb.prod_est, eb.pr_venda
            FROM est_basico eb
            LEFT JOIN dfb_estoque dfb ON eb.id_item = dfb.fk_est_basico
            WHERE dfb.cod_ean = $1 OR eb.bar_code = $2 OR eb.nom_item = $3
            LIMIT 1
        `

		row := r.db.QueryRow(query, codEAN, barCode, nomItem)

		var d domain.DuplicataEstoque
		var codEANNull sql.NullString

		err := row.Scan(
			&d.SIDItem,
			&d.SNomItem,
			&d.SBarCode,
			&codEANNull,
			&d.SProdEst,
			&d.SPrVenda,
		)

		if err == nil {
			if codEANNull.Valid {
				d.SCodEAN = codEANNull.String
			} else {
				d.SCodEAN = ""
			}
			d.XMLItemID = xmlItemID // Associa o ID do XML

			log.Printf("[DUPLICATA ENCONTRADA] ID: %d | Nome: %s | BAR_CODE: %s | EAN: %s | Qtd: %d | Preço: %d | XML Item ID: %d",
				d.SIDItem, d.SNomItem, d.SBarCode, d.SCodEAN, d.SProdEst, d.SPrVenda, d.XMLItemID)

			duplicatas = append(duplicatas, d)

		} else if errors.Is(err, sql.ErrNoRows) {
			log.Printf("[SEM DUPLICATA] Nenhum resultado para Nome: %s | BAR_CODE: %s | EAN: %s", nomItem, barCode, codEAN)
		} else {
			log.Printf("[ERRO] Erro ao executar consulta para Nome: %s | Erro: %v", nomItem, err)
		}
	}

	log.Printf("[DEBUG] Verificação concluída. Total de duplicatas encontradas: %d", len(duplicatas))
	return duplicatas
}

// Busca um JSON específico salvo no banco pelo id_json
func (r *ProdutoNFeRepository) BuscarJSONPorID(id int) ([]map[string]interface{}, error) {
	query := `SELECT t_json FROM temp_json WHERE id_json = $1`

	var raw []byte
	err := r.db.QueryRow(query, id).Scan(&raw)
	if err != nil {
		return nil, fmt.Errorf("erro ao buscar JSON: %w", err)
	}

	var result []map[string]interface{}
	if err := json.Unmarshal(raw, &result); err != nil {
		return nil, errors.New("erro ao decodificar JSON armazenado")
	}

	return result, nil
}
