
import Card from "../Card"

export function PredictionResults({ prediction, error, loading }) {
    const hasResult = prediction !== null || error !== null;
    const isIdle = !loading && !hasResult;

    return (
        <>
            <h1>Predictions</h1>

            <Card display="flex-col">
                {loading ? (
                    <h2>Generating predictions...</h2>
                )  : isIdle ? (
                    <h2 className="default-prediction-text">Select Teams to generate a prediction</h2>
                )  : (
                    <h2>IT worked!</h2>
                )}
            </Card>
        </>
    )
}