#include<bits/stdc++.h>
using namespace std;

void solve(int n,int* arr){
    int j=0;
    int i=n-1;
    vector<int>ans;
    while(j<i){
        while(arr[j] ==0 && j < i){
            j++;
        }
        while(arr[i] ==1 && j < i){
            i--;
        }
        if(j < i){   // we  need to swap the arr[j] and arr[i]
            arr[j] =0;
            arr[i] =1;
            j++;
            i--;
        }
    } 
    return;
}

int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    solve(n,arr);
    for(int i=0;i<n;i++){
        cout<<arr[i]<<" ";
    }
}