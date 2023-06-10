// input : aac
// output : ab a aab aa  b , plz chek out the video again this imp question   
// 

/* Given an array of integers that might contain duplicates, return all possible subsets.

Note:

        Elements in a subset must be in non-descending order.
        The solution set must not contain duplicate subsets.
        The subsets must be sorted lexicographically.
*/


#include<bits/stdc++.h>

using namespace std;
void solve(string ip,string op,vector<string>&vec) {
    if(ip.length()==0){
       vec.push_back(op);
        return;
    }
    string op1=op;    // set the values to output string
    string op2=op;    // same as 
    op2.push_back(ip[0]);  // push the first element into the other output
    ip.erase(ip.begin() + 0); //erase the 0th index of the string 
    solve(ip,op1,vec);     //pass the values it recursion will do its work
    
    solve(ip,op2,vec);
    return;
}
int main() 
{
    string s1;
    cin >> s1;
    string s2 =""; // for output purpose
    unordered_set<string> set;   //for ordered output we can use set also
    vector<string> vec;
    solve(s1,s2,vec);

    for(int i=0;i<vec.size();i++) {
        set.insert(vec[i]);
    }
    
    for(auto it=set.begin(); it!=set.end(); it++) {
        cout<< *it<<" ";
    }
    
}

