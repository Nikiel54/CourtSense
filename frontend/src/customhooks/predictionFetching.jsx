import { useEffect } from "react";
import { useState } from "react";


export const usePredictions = ( homeId, awayId, isSubmitted, onFetchComplete ) => {
    const [prediction, setPrediction] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const predictUrl = 'http://127.0.0.1:8000/apis/prediction' // use .env here


    useEffect(() => {
        async function fetchPredictions () {
            try {
                setLoading(true); // now begin fetching

                const response = await fetch(predictUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        "home_team_id": homeId,
                        "away_team_id": awayId,
                    })
                });

                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`)
                }

                const data = await response.json();
                setPrediction(data); // update state with new data
            } catch (error) {
                setError(error);
            } finally {
                setLoading(false);
                if (onFetchComplete) {
                    onFetchComplete();
                }
            }
        }
        
        if (isSubmitted && homeId && awayId) {
            fetchPredictions();
        } else {
            return;
        }

    }, [isSubmitted, awayId, homeId, onFetchComplete])

    return { prediction, error, loading };
}