/* Target Sum Problem
Given a list of non-negative integers, a1, a2, ..., an, and a target, S. Now you have 2 symbols + and -. For each integer, you should choose one from + and - as its new symbol.

Find out how many ways to assign symbols to make sum of integers equal to target S.

Example 1:
Input: nums is [1, 1, 1, 1, 1], S is 3. 
Output: 5
Explanation: 

-1+1+1+1+1 = 3
+1-1+1+1+1 = 3
+1+1-1+1+1 = 3
+1+1+1-1+1 = 3
+1+1+1+1-1 = 3

There are 5 ways to assign symbols to make the sum of nums be target 3.*/


// THIS IS THE exact same question as the last one 
// just asked in the diffrent tricky manner 
// just chek out the video again if u want to


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