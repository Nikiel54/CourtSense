import Card from "../layout/Card";
import PredictionContents from "./PredictionContents";


export function PredictionResults({ prediction, error, loading, teamData }) {
    const hasResult = prediction !== null; // successful fetch
    const hasError = error !== null;
    const isIdle = !loading && !hasResult; // is true before data is even fetched

    return (
        <>
            <h1>Predictions</h1>

            <Card display="flex-col">
                {isIdle ? (
                    <h2 className="default-prediction-text">Select Teams to generate a prediction</h2>
                )  : (hasError ? (
                    <h2>{`Error occured: ${error.message}`}</h2>
                )  : (hasResult ? (
                    <PredictionContents 
                        key={`${prediction.home_team_id}-${prediction.away_team_id}`}
                        prediction={prediction} 
                        teamData={teamData} 
                    />
                )  : (
                    <h2>Internal error!</h2>
                )))}
            </Card>
        </>
    )
}