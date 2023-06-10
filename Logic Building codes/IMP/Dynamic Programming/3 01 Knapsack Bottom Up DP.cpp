#include<bits/stdc++.h>
// BOTTOM UP 
using namespace std;
int static t[1000][1000];  /* simply initilize it to array of size n+1,W+1 but i don't know 
how to do it,this is important step  */

int solve(int val[],int wt[],int W,int n) {

    /*int t[n+1][W+1]; i didn't get how to initilize it

    if(n == 0 || W == 0) {  // when the weight or number  of items becomes 0, we return 0
        return 0;
    }  down step is similar*/

    /****** REMEMBER FOR EVERY 'n' we have to put 'i' and for every 'W'->'j' ******/

    for(int i =0;i<n+1;i++){
        for(int j =0;j<W+1;j++){
            if(n==0 || W==0){

                t[i][j] = 0; /* as we do in recursion we define Base value/step 
                this is that step */
            }
        }
    }
    for(int i =1;i<n+1;i++){
        for(int j =1;j<W+1;j++){
            /* 
            if(wt[n-1] <= W) {
            return max(val[n-1] + solve(val,wt,W-wt[n-1],n-1),solve(val,wt,W,n-1));
            we want the sum of maximum values we can store it into the knapsack*/
            if(wt[i-1] <= j ) {
                t[i][j] = max(val[i-1] + t[i-1] [j-wt[i-1]],
                            t[i-1][j] );
            }
            /* 
            else if (wt[n-1] > W) {
                return solve(val,wt,W,n-1) // down below is same step
            }
             */
            else if (wt[i-1] > j ) {
                t[i][j] = t[i-1][j];
            }
        }
    }

    return t[n][W];  // by this we'll return the value we want 

}

int main() 
{
    int n;
    cin>> n;
    int W; 
    cin>>W;
    int val[n];
    int wt[n];
    for(int i=0;i<n;i++) {
        cin>>val[i];
    }
    for(int i =0;i<n;i++) {
        cin>>wt[i];
    }
    cout<<solve(val,wt,W,n);
}