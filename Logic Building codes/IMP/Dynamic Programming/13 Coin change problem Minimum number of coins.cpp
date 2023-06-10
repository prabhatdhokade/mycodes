/* Coin Change Problem(contd)
 before this video,see this................first.
Given a value V, if we want to make change for V cents, and we have infinite supply of 
each of C = { C1, C2, .. , Cm} valued coins, what is the minimum number of coins to make 
the change?
Examples:

Input: coins[] = {25, 10, 5}, V = 30
Output: Minimum 2 coins required
We can use one coin of 25 cents and one of 5 cents 

VERY VERY IMPORTANT QUESTION

*/

#include<bits/stdc++.h>

using namespace std;

int solve(int coin[],int n,int sum){


    int t[n+1][sum+1];
    for(int i =0;i<n+1;i++){
        for(int j=0;j<sum+1;j++){
            if( j==0){
                t[i][j] = 0;
            }
            if(i==0){
                t[i][j] = INT_MAX-1;    // we have to intitilize it beacuse in line no 31 we did 
            }   // 1+t[i][j-arr[i-1]],if we get that value then INT_MAX+1 becomes negative value
                //so if subtract -1 from INt_MAX -1+1 will get cancelled
        }
    }

    for(int j=1;j<sum+1;j++){    //this is IMP step this the step which extra in this question
        if(j % coin[0] == 0){  
            t[1][j] = j/coin[0];  // why do we intitlize the 2nd row of matrix
        }                          // just try it on papaer or watch the video once
        else 
            t[1][j] = INT_MAX-1;
    }

    for(int i=2;i<n+1;i++){
        for(int j=1;j<sum+1;j++){
            if(coin[i-1] <= j){
                t[i][j]= min( 1 + t[i][j-coin[i-1]] , t[i-1][j]); // we did +1 beacuse we'll get negative value and that will be the minimum value
            }
            else if(coin[i-1] > j){
                t[i][j] = t[i-1][j];
            }
            else 
                return -1;
        }   

    }
    if(t[n][sum] == INT_MAX -1){ // for returning -1 we did tgis step
        return -1;
    }
    else
        return t[n][sum];

}

int main()
{
    int n;
    cin>>n;
    int sum;
    cin>>sum;
    int coin[n];
    for(int i=0;i<n;i++){
        cin>>coin[i];
    }
    cout<<solve(coin,n,sum);
}