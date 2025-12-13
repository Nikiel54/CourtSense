##### API V1 FOR PREDICTION API ENDPOINTS ####


from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.prediction_service import PredictionService, get_prediction_service

router = APIRouter()

class PredictionRequest(BaseModel):
    home_team_id: int
    away_team_id: int



@router.post('/prediction')
async def predict_winner(
    prediction_request: PredictionRequest,
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    '''
    Endpoint defines how to handle a prediction request between two teams
    '''
    try:
        prediction = prediction_service.make_prediction(
            prediction_request.home_team_id,
            prediction_request.away_team_id
        )

        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get('/teamnames')
async def get_team_names(
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    return {
        'team_names': prediction_service.get_team_names(),
    }
    

@router.get('/rating/{team_id}')
async def get_team_rating(
    team_id: int,
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    '''
    Endpoint for GET requests on a single team's rating
    '''
    rating = round(prediction_service.get_team_rating(team_id=team_id), 0)

    return {
        'team_id': team_id,
        'rating': rating
    }


@router.get('/ratings')
async def get_team_ratings(
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    '''
    Endpoint for GET requests on getting all team elo ratings
    '''

    all_team_ratings = prediction_service.get_all_ratings()

    return all_team_ratings


