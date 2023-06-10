/* 
Problem Description:

Given an array containing N positive integers and an integer K. Your task is to find the length of the longest Sub-Array with sum of the elements equal to the given value K.

For Input:

7 
4 1 1 1 2 3 5
5
your output is: 
4*/

// THIS CODE ONLY WORKS ON POSITIVE NUMBERS PS!!!!!!!!!!!! 

#include<bits/stdc++.h>

using namespace std;

int solve(int n,int arr[],int k){
    int i=0,j=0;
    int ans = 0;
    int sum=0;
    while(j<n){
        
        sum += arr[j];
        
        if(sum < k){
            j++;
        }

        /*else if(sum == k) {    // this is of aditya's code and  below's yours
            ans = max(ans,j-i+1);
            j++; 
        }
        else if(sum > k) {
            
            while(sum>k){
            sum -= arr[i];
            i++;
            } 
            j++; 
        }  */

        else if( sum >= k){
            if(sum == k){
                ans = max(ans,j-i+1);
            }
            sum -= arr[i];
            i++;
            j++;
        }
    }
    return ans;
}

int main() {
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    int k;
    cin>>k;
    cout<< solve(n,arr,k);
} 