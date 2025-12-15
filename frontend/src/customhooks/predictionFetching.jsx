import { useEffect } from "react";
import { useState } from "react";


export const usePredictions = ( homeId, awayId, isSubmitted, onFetchComplete ) => {
    const [prediction, setPrediction] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const serverBaseUrl = import.meta.env.VITE_SERVER_APIS_BASE_URL;
    const predictUrl = `${serverBaseUrl}prediction`;


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

    }, [isSubmitted, awayId, homeId, onFetchComplete, predictUrl])

    return { prediction, error, loading };
}