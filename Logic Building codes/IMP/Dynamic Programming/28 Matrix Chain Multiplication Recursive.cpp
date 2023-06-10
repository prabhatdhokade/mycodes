/*Given a sequence of matrices, find the most efficient way to multiply these matrices together. The efficient way is the one that involves the least number of multiplications.

The dimensions of the matrices are given in an array arr[] of size N (such that N = number of matrices + 1) where the ith matrix has the dimensions (arr[i-1] x arr[i]).

Example 1:

Input: N = 5
arr = {40, 20, 30, 10, 30}
Output: 26000
Explaination: There are 4 matrices of dimension 
40x20, 20x30, 30x10, 10x30. Say the matrices are 
named as A, B, C, D. Out of all possible combinations,
the most efficient way is (A*(B*C))*D. 
The number of operations are -
20*30*10 + 40*20*10 + 40*10*30 = 26000.

Example 2:

Input: N = 4
arr = {10, 30, 5, 60}
Output: 4500
Explaination: The matrices have dimensions 
10*30, 30*5, 5*60. Say the matrices are A, B 
and C. Out of all possible combinations,the
most efficient way is (A*B)*C. The 
number of multiplications are -
10*30*5 + 10*5*60 = 4500.

https://practice.geeksforgeeks.org/problems/matrix-chain-multiplication0303/1#
*/


#include<bits/stdc++.h>
using namespace std;

int solve(int arr[],int i,int j) {
    if(i>=j) {    // At i == j the cost is zero not because there's only one element in the array. It'll be because there's no other matrix to which the remaining matrix will be multiplied
        return 0;
    }
    int min = INT_MAX; // as in the question we need to find minimum value

    for(int k= i; k<j;k++) {
        int temp_ans = solve(arr,i,k) + solve(arr,k+1,j) + arr[i-1] * arr[k] * arr[j]; //this the main heart of the problem there we have to break in parts,we need to multiply in with i t0 k then k+1 t0 j;do it on papaer or wtch video

        if(temp_ans < min) {
            min = temp_ans;
        } 
    } 
    return min; 

   /*  for(int k = i+1; k<=j;k++) {    // this has to be a another condition but something went wrong
        int temp_ans = solve(arr,i,k-1) + solve(arr,k,j) + arr[i-1] * arr[k] * arr[j];

        if(temp_ans < min) {
            min = temp_ans;
        }
    } */
   
}

int mcm(int arr[],int n) {
    int i =1;    // why i =1 you may have question, to make matrix ai = arr[i-1] * arr[i] will be the dimenssions  ,if we take i=0;then arr[-1] is not possible so we cannot take that as a i =0; 
    int j =n-1;  // as ususal j is last most index of arr
    return solve(arr,i,j);
}


int main() 
{
    int n;
    cin>>n;
    int arr[n];
    for(int i =0;i<n;i++) {
        cin>>arr[i];
    }
    cout<<mcm(arr,n);
}