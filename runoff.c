#include <cs50.h>
#include <stdio.h>
#include <string.h>

// Max voters and candidates
#define MAX_VOTERS 100
#define MAX_CANDIDATES 9

// preferences[i][j] is jth preference for voter i
int preferences[MAX_VOTERS][MAX_CANDIDATES];

// Candidates have name, vote count, eliminated status
typedef struct
{
    string name;
    int votes;
    bool eliminated;
}
candidate;

// Array of candidates
candidate candidates[MAX_CANDIDATES];

// Numbers of voters and candidates
int voter_count;
int candidate_count;

// Function prototypes
bool vote(int voter, int rank, string name);
void tabulate(void);
bool print_winner(void);
int find_min(void);
bool is_tie(int min);
void eliminate(int min);

int main(int argc, string argv[])
{
    // Check for invalid usage
    if (argc < 2)
    {
        printf("Usage: runoff [candidate ...]\n");
        return 1;
    }

    // Populate array of candidates
    candidate_count = argc - 1;
    if (candidate_count > MAX_CANDIDATES)
    {
        printf("Maximum number of candidates is %i\n", MAX_CANDIDATES);
        return 2;
    }
    for (int i = 0; i < candidate_count; i++)
    {
        candidates[i].name = argv[i + 1];
        candidates[i].votes = 0;
        candidates[i].eliminated = false;
    }

    voter_count = get_int("Number of voters: ");
    if (voter_count > MAX_VOTERS)
    {
        printf("Maximum number of voters is %i\n", MAX_VOTERS);
        return 3;
    }

    // Keep querying for votes
    for (int i = 0; i < voter_count; i++)
    {

        // Query for each rank
        for (int j = 0; j < candidate_count; j++)
        {
            string name = get_string("Rank %i: ", j + 1);

            // Record vote, unless it's invalid
            if (!vote(i, j, name))
            {
                printf("Invalid vote.\n");
                return 4;
            }
        }
        printf("\n");
    }

    // Keep holding runoffs until winner exists
    while (true)
    {
        // Calculate votes given remaining candidates
        tabulate();

        // Check if election has been won
        bool won = print_winner();
        if (won)
        {
            break;
        }

        // Eliminate last-place candidates
        int min = find_min();
        bool tie = is_tie(min);

        // If tie, everyone wins
        if (tie)
        {
            for (int i = 0; i < candidate_count; i++)
            {
                if (!candidates[i].eliminated)
                {
                    printf("%s\n", candidates[i].name);
                }
            }
            break;
        }

        // Eliminate anyone with minimum number of votes
        eliminate(min);

        // Reset vote counts back to zero
        for (int i = 0; i < candidate_count; i++)
        {
            candidates[i].votes = 0;
        }
    }
    return 0;
}

// Record preference if vote is valid
bool vote(int voter, int rank, string name)
{
    // loop over all the candidates, valid preference is recorded via strcmp between the inputted name and all the candidates from the list; otherwise programs exits
    for (int k = 0; k < candidate_count; k++)
    {
        if (strcmp(name, candidates[k].name) == 0)
        {
            preferences[voter][rank] = k;
            return true;
        }
    }
    return false;
}

// Tabulate votes for non-eliminated candidates
void tabulate(void)
{
    // k is initialized in order to be used in outer loops later on
    int k = 0;
    // two nested for loops in order to capture preferences[i][j] and last one for k in order to find a match for each voter
    for (int i = 0; i < voter_count; i++)
    {
        for (int j = 0; j < candidate_count; j++)
        {
            for (k = 0; k < candidate_count; k++)
            {
                // if k'th candidate is not eliminated and k matches the current preferences index, go ahead and add vote to the candidate and break out of the k loop
                if (!candidates[k].eliminated)
                {
                    if (k == preferences[i][j])
                    {
                        candidates[k].votes++;
                        break;
                    }
                }
            }
            // if k matches preferences another break has to be used in order to get to another voter (i.e. the i for loop);
            if (k == preferences[i][j])
            {
                break;
            }
        }
    }
}
// Print the winner of the election, if there is one
bool print_winner(void)
{
    // goes over candidate count, if vote total more than half of the voters, declare winner
    for (int i = 0; i < candidate_count; i++)
    {
        if (candidates[i].votes > (voter_count / 2))
        {
            printf("%s\n", candidates[i].name);
            return true;
        }
    }
    return false;
}

// Return the minimum number of votes any remaining candidate has
int find_min(void)
{
    // minimum is initialized to 0
    int minimum = 0;
    // loop is used to find and ultimately return the lowest possible vote total
    for (int j = 0; j < candidate_count - 1; j++)
    {
        if (!candidates[j].eliminated && !candidates[j + 1].eliminated)
        {
            // if j'th candidate's vote total is higher or equal to j+1'th candidate's vote total, go ahead and make j+1'th vote total the new minimum
            if (candidates[j + 1].votes <= candidates[j].votes)
            {
                minimum = candidates[j + 1].votes;
            }
        }
    }
    return minimum;
}

// Return true if the election is tied between all candidates, false otherwise
bool is_tie(int min)
{
    // loop goes over all candidates, if a candidate is not eliminated and his vote total does not equal minimum is_tie returns false
    for (int i = 0; i < candidate_count; i++)
    {
        if (!candidates[i].eliminated)
        {
            if (candidates[i].votes != min)
            {
                return false;
            }
        }
    }
    return true;
}

// Eliminate the candidate (or candidiates) in last place
void eliminate(int min)
{
    // goes over candidates, if any candidate's vote total equals minimum, the eliminated value turns to true
    for (int i = 0; i < candidate_count; i++)
    {
        if (candidates[i].votes == min)
        {
            candidates[i].eliminated = true;
        }
    }
    return;
}
