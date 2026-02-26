package main

import (
	"log"

	"projeto_troca_de_oleo/internal/config"
	"projeto_troca_de_oleo/internal/handler"
	"projeto_troca_de_oleo/internal/repository"

	"github.com/gin-gonic/gin"
)

func main() {
	gin.SetMode(gin.DebugMode) // Mudado para DebugMode para logs detalhados
	router := gin.Default()

	// Conexão com o banco via database/sql
	db, err := config.OpenDBConnection()
	if err != nil {
		log.Fatalf("Erro ao conectar ao banco de dados: %v", err)
	}
	defer db.Close()

	// Registro da rota de execução da NF-e
	produtoNFeRepo := repository.NewProdutoNFeRepository(db)
	handler.RegisterProdutoNFeRoutes(router, produtoNFeRepo)

	log.Fatal(router.Run(":8080"))
}
