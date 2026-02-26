package security

import (
	"regexp"
	"strings"
)

var suspiciousPatterns = []string{
	`(?i)'\s*or\s+'`,
	`(?i)"\s*or\s+"`,
	`(?i)or\s+\d+=\d+`,
	`(?i)union\s+select`,
	`(?i)select\s+.+\s+from`,
	`(?i)drop\s+table`,
	`(?i)insert\s+into`,
	`(?i)update\s+\w+\s+set`,
	`(?i)delete\s+from`,
	`--`,
	`;`,
}

// IsSQLInjection verifica se uma string parece conter SQL Injection
func IsSQLInjection(input string) bool {
	cleanInput := strings.TrimSpace(input)
	for _, pattern := range suspiciousPatterns {
		if matched, _ := regexp.MatchString(pattern, cleanInput); matched {
			return true
		}
	}
	return false
}

func IsPlacaSegura(placa string) bool {
	placa = strings.ToUpper(strings.TrimSpace(placa))
	re := regexp.MustCompile(`^[A-Z]{3}[0-9]{4}$|^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$`)
	return re.MatchString(placa)
}
