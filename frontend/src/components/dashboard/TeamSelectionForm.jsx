
export function TeamSelectionForm({
    teamData, 
    homeTeam, 
    setHomeTeam, 
    awayTeam, 
    setAwayTeam, 
    homeTeamError, 
    setHomeTeamError,
    awayTeamError,
    setAwayTeamError,
    sameTeamSelectionError,
}) {
    return (
        <>
            <div>
                <label>
                    Home Team
                    <button type="button" className="selection-btn">
                        <select
                            name="Home Team"
                            value={homeTeam === "" ? "" : homeTeam.name}
                            onChange={(e) => {
                                if (e.target.value === "") {
                                    setHomeTeam("");
                                } else {
                                    setHomeTeam(teamData.find((team) => team.name === e.target.value));
                                    setHomeTeamError(false);
                                }
                            }}>
                            <option key="0" value="">Select a team</option>
                            {teamData.map((team) => {
                                return (
                                    <option key={team.id} value={team.name}>{team.name}</option>
                                )
                            })}
                        </select>
                    </button>
                </label>
                {homeTeamError ? (
                    <strong className="error-txt">Missing Home Team!</strong>) 
                : (sameTeamSelectionError ? ( // we render err text since they selected the same two teams
                    <strong className="error-txt">Can't Select Same Teams!</strong>
                ) : (null) // nothing to render
                )}
            </div>
            <div>
                <label>
                    Away Team
                    <button type="button" className="selection-btn">
                        <select
                            name="Away Team"
                            value={awayTeam === "" ? "" : awayTeam.name}
                            onChange={(e) => {
                                if (e.target.value === "") {
                                    setAwayTeam("");
                                } else {
                                    setAwayTeam(teamData.find((team) => team.name === e.target.value));
                                    setAwayTeamError(false);
                                }
                            }}>
                            <option key="0" value="">Select a team</option>
                            {teamData.map((team) => {
                                return (
                                    <option key={team.id} value={team.name}>{team.name}</option>
                                )
                            })}
                        </select>
                    </button>
                </label>
                {awayTeamError ? (
                    <strong className="error-txt">Missing Away Team!</strong>) 
                : (sameTeamSelectionError ? ( // we render err text since they selected the same two teams
                    <strong className="error-txt">Can't Select Same Teams!</strong>
                ) : (null) // nothing to render
                )}
            </div>
        </>
                    
    )
}