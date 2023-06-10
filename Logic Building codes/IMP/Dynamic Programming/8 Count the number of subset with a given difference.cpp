/* Count the subsets with given difference

input : 4 
        1
        1 1 2 3
output : 3*/

#include<bits/stdc++.h>

using namespace std;

int count(int arr[],int n, int s1){ // count of the subset with given sum
    int t[n+1][s1+1];

    for(int i=0;i<n+1;i++){
        for(int j=0;j<s1+1;j++){
            if( i ==0){
                t[i][j] = 0;
            }
            if(j ==0){
                t[i][j] = 1;
            }
        }
    }

    for(int i =1;i<n+1;i++){
        for(int j =1;j<s1+1;j++){
            if(arr[i-1] <= j){
                t[i][j] = t[i-1][j] + t[i-1][j-arr[i-1]];
            }
            else 
                t[i][j] = t[i-1][j];
        }
    }

    return t[n][s1];
}

int solve(int arr[],int n,int diff){
    int sum =0;
    int s1=0;
    for(int i=0;i<n;i++){
        sum += arr[i];  
    }
    s1 = (sum + diff) /2;   // this is basic maths s1-s2 = diff , s1+s2 == sum of array
    return count(arr,n,s1); // add both the equations we'll get 2s1= sum+ diff
    // and then we solved the same thing in previous question. count
}

int main() 
{
    int n ;
    cin >> n;
    int diff;
    cin>>diff;
    int arr[n];
    for(int i =0;i<n;i++){
        cin>>arr[i];
    }

    cout<<solve(arr,n,diff);
}