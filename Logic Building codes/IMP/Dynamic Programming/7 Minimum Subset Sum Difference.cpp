/* Sum of subset differences
Given a set of integers, the task is to divide it into two sets S1 and S2 such that the
 absolute difference between their sums is minimum.
If there is a set S with n elements, then if we assume Subset1 has m elements, Subset2 
must have n-m elements and the value of abs(sum(Subset1) – sum(Subset2)) should be 
minimum.

Example:
Input:  arr[] = {1, 6, 11, 5} 
Output: 1
Explanation:
Subset1 = {1, 5, 6}, sum of Subset1 = 12 
Subset2 = {11}, sum of Subset2 = 11 

PROBLEM STATEMENT LINK:https://practice.geeksforgeeks.org/problems/minimum-sum-partition3317/1  */

/***** MOST IMPORTANT QUESTION ****** HARD level */


#include<bits/stdc++.h>

using namespace std;

bool SubSetSum(int arr[],int n,int range,vector<int>&v) { //this is same as subset sum problem
    bool t[n+1][range+1];
    for(int i =0;i<n+1;i++){
        for(int j =0;j<range+1;j++){
            if(i==0){
                t[i][j] = false;
            }
            if(j==0){
                t[i][j] = true;
            }
        }
    }

    for(int i =1;i<n+1;i++){
        for(int j=1;j<range+1;j++){
            if(arr[i-1] <= j) {
                t[i][j] = t[i-1][j] || t[i-1][j-arr[i-1]];
            }
            else if(arr[i-1] > j) {
                t[i][j] = t[i-1][j];
            }
        }
    }

    for(int j=0;j<=range/2;j++){ // i need to go only till half i can derive s2 from s1. and i'm assuring that s1 always have to be smaller than s2
        if(t[n][j] == true){     // t[n] this is the imp step,that thing fucked the ans for 4 hours.
            v.push_back(j); 
        }
    }
    return t[n+1][range+1];
}


int solve(int arr[],int n){
    int range = 0;  // found out the range in that the solution will lie in
    for(int i =0;i<n;i++) {
        range += arr[i]; //total sum of the array
    }
    vector<int> v; //for subset s1

    SubSetSum(arr,n,range,v);  // we have to find out that how many 

    int mn=INT_MAX; // minimum value

    for(int i=0;i<v.size();i++) {   // we need to find minnimum diff
        mn= min(mn,range - 2*v[i]);   // range = s1+s2 ,i.e. s2= range-s1 , diff = s2-s1
    }                                  // so. diff=range-s1-s1 , diff = range -2s1;  
    return mn;
}


int main()
{   
    int n;
    cin>>n;
    int arr[n];
    for(int i =0;i<n;i++) {
        cin>>arr[i];
    }
    cout<<solve(arr,n);

}   