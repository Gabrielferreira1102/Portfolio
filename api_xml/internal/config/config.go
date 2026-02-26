package config

import (
	"database/sql"
	"log"

	_ "github.com/lib/pq"
)

// GetDBConnString retorna a string de conexão diretamente no código
func GetDBConnString() string {
	//aqui é só prencher com o seu banco
	return "user= password= dbname= sslmode= host="
}

// OpenDBConnection abre conexão com database/sql
func OpenDBConnection() (*sql.DB, error) {
	connStr := GetDBConnString()
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Printf("Erro ao abrir conexão com o banco: %v", err)
		return nil, err
	}
	return db, nil
}
