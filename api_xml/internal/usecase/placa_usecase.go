package usecase

import (
	"projeto_troca_de_oleo/internal/domain"
)

type placaUsecase struct {
	repo domain.PlacaRepository
}

func NewPlacaUsecase(r domain.PlacaRepository) domain.PlacaUsecase {
	return &placaUsecase{repo: r}
}

func (uc *placaUsecase) BuscarPorPlaca(placa string) (*domain.Veiculo, error) {
	return uc.repo.FindByPlaca(placa)
}
